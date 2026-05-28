import asyncio
import functools

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .avas import check_img
from .pg import check_rel, filter_target_user, rem_session
from .tools import (
    check_g_secure, check_permissions, check_profile_permissions, check_secure)


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
