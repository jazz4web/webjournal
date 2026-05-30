import asyncio
import functools

from datetime import datetime, UTC

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .avas import check_img
from .pg import check_data, check_rel, filter_target_user, rem_session
from .tasks import send_mail_mail
from .tools import (
    check_g_secure, check_permissions, check_profile_permissions, check_secure)


class ChangeM(HTTPEndpoint):
    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        address, passwd, auth = (
            d.get('address'), d.get('passwd'), d.get('auth'))
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        if not all((address, passwd, auth)):
            res['message'] = 'Отправленные данные не прошли проверку.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, auth)
        if cu is None:
            res['message'] = 'Действие требует авторизации.'
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cue)
            await conn.close()
            return JSONResponse(res)
        if pbkdf2_sha256.verify(
                passwd, await conn.fetchval(
                    'SELECT password_hash FROM users WHERE id = $1',
                    cu.get('id'))):
            message = await check_data(
                request.app.config, conn, cu.get('id'), address)
            if message:
                res['message'] = message
                await conn.close()
                return JSONResponse(res)
            asyncio.ensure_future(
                send_mail_mail(request, address, cu))
            res['done'] = True
            await set_flashed(
                request, 'На ваш новый адрес выслано письмо с инструкциями.')
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        res['message'] = 'Пароль недействителен.'
        return JSONResponse(res)


class ChangePasswd(HTTPEndpoint):
    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        passwd, newpwd, confirma, auth = (
            d.get('passwd'), d.get('newpwd'),
            d.get('confirma'), d.get('auth'))
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        if not all((passwd, newpwd, confirma, auth)):
            res['message'] = 'Ваши данные не прошли проверку.'
            return JSONResponse(res)
        if newpwd != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, auth)
        if cu is None:
            res['message'] = 'Действие требует авторизации.'
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        if pbkdf2_sha256.verify(
                passwd, await conn.fetchval(
                    'SELECT password_hash FROM users WHERE id = $1',
                    cu.get('id'))):
            await conn.execute(
                '''UPDATE users SET password_hash = $1, last_visit = $2
                     WHERE id = $3''',
                pbkdf2_sha256.hash(newpwd), datetime.now(UTC), cu.get('id'))
            await set_flashed(request, 'У вас новый пароль.')
            res['done'] = True
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        res['message'] = 'Пароль недействителен.'
        return JSONResponse(res)


class ChangeAva(HTTPEndpoint):
    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        img, auth = d.get('image'), d.get('token')
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, auth)
        if cu is None:
            res['message'] = 'Действие требует авторизации.'
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        if not img:
            res['message'] = 'Требуется файл изображения.'
            await conn.close()
            return JSONResponse(res)
        binary = await img.read()
        await img.close()
        if len(binary) > 200 * 1024:
            res['message'] = 'Недопустимый размер файла.'
            await conn.close()
            return JSONResponse(res)
        loop = asyncio.get_running_loop()
        img = await loop.run_in_executor(
            None, functools.partial(check_img, binary))
        if img is None:
            res['message'] = 'Файл не соответствует заданным условиям.'
            await conn.close()
            return JSONResponse(res)
        uid = await conn.fetchval(
            'SELECT user_id FROM avatars WHERE user_id = $1', cu.get('id'))
        if uid:
            await conn.execute(
                'UPDATE avatars SET picture = $1 WHERE user_id = $2',
                img, uid)
        else:
            await conn.execute(
                'INSERT INTO avatars (picture, user_id) VALUES ($1, $2)',
                img, cu.get('id'))
        await conn.close()
        res['done'] = True
        await set_flashed(request, 'Аватар изменён, обновите кэш браузера.')
        return JSONResponse(res)


class Profile(HTTPEndpoint):
    async def get(self, request):
        res = {'user': None, 'cu': None}
        token = request.headers.get('x-auth-sestee')
        username = request.query_params.get('username')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 0)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if cu and username:
            target = await filter_target_user(request, conn, username)
            if target is None:
                res['message'] = f'{username}? Не знаем такого...'
                await conn.close()
                return JSONResponse(res)
            res['user'] = target
            rel = await check_rel(conn, cu.get('id'), target.get('uid'))
            await check_profile_permissions(cu, target, res, rel)
            if res['address']:
                res['user']['address'] = await conn.fetchval(
                    'SELECT address FROM accounts WHERE user_id = $1',
                    target.get('uid'))
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 100):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        text = d.get('text')
        if text:
            await conn.execute(
                'UPDATE users SET description = $1 WHERE id = $2',
                text.strip()[:500], cu.get('id'))
        else:
            await conn.execute(
                'UPDATE users SET description = $1 WHERE id = $2',
                None, cu.get('id'))
        await conn.close()
        res['done'] = True
        await set_flashed(request, 'Описание блога обновлено.')
        return JSONResponse(res)
