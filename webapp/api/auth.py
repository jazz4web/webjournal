import asyncio
import re

from datetime import datetime, UTC

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.attri import USERNAME_PATTERN
from ..auth.pg import check_username
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .redi import extract_cache
from .pg import check_acc, check_address, create_session, filter_user
from .tasks import (
    change_pattern, create_user, rem_old_session, send_reg_mail, send_rfp_mail)
from .tokens import check_token, create_login_token
from .tools import check_secure, fix_bad_token

BADCAPTCHA = 'Неверный код, повторите попытку.'


class CreateAcc(HTTPEndpoint):
    async def get(self, request):
        res = {'aid': None}
        token = request.headers.get('x-rfp-token')
        if token is None:
            raise HTTPException(403)
        acc = await check_token(request.app.config, token)
        if acc is None:
            res['message'] = await fix_bad_token(request.app.config)
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            'SELECT id, address, user_id FROM accounts WHERE id = $1',
            acc.get('aid'))
        await conn.close()
        if acc is None:
            res['message'] = await fix_bad_token(request.app.config)
            return JSONResponse(res)
        if acc and acc.get('user_id'):
            res['message'] = 'Пользователь на этом аккаунте уже создан.'
            return JSONResponse(res)
        res['aid'] = True
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': False}
        d = await request.form()
        address, cache, captcha = (
            d.get('address'), d.get('cache'), d.get('captcha'))
        if not all((address, cache, captcha)):
            res['message'] = 'Данные не соответствуют запросу.'
            return JSONResponse(res)
        suffix, val = await extract_cache(request, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        message, account = await check_address(request, conn, address)
        await conn.close()
        if message or (account and account.get('user_id')):
            orm = 'Аккаунт уже существует, пароль можно восстановить.'
            res['message'] = message or orm
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        res['done'] = True
        asyncio.ensure_future(
            change_pattern(request.app.config, suffix))
        asyncio.ensure_future(
            send_reg_mail(request, address))
        await set_flashed(
            request, 'На Ваш адрес выслано письмо с инструкциями.')
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        username, passwd, confirma = (
            d.get('username'), d.get('passwd'), d.get('confirma'))
        if not all((username, passwd, confirma)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        p = re.compile(USERNAME_PATTERN)
        if not p.match(username):
            res['message'] = '''Псевдоним должен быть от 3 до 16 символов
            (буквы латинского или русского алфавитов, цифры, точка, дефис,
            нижнее подчёркивание) и начинаться с буквы.'''
            return JSONResponse(res)
        if await check_username(request.app.config, username):
            res['message'] = '''Этот псевдоним уже зарегистрирован,
            выберите другой.'''
            return JSONResponse(res)
        if passwd != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        acc = await check_token(request.app.config, d.get('key'))
        if acc is None:
            res['message'] = 'Брелок недействителен.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            'SELECT id, user_id FROM accounts WHERE id = $1',
            acc.get('aid'))
        await conn.close()
        if acc is None or acc.get('user_id'):
            res['message'] = 'Данные неверны, действие отменено.'
            return JSONResponse(res)
        asyncio.ensure_future(
            create_user(request, username, passwd, acc.get('id')))
        res['done'] = True
        await set_flashed(
            request, f'Аккаунт {username} успешно создан, вы можете войти.')
        return JSONResponse(res)


class ResetFP(HTTPEndpoint):
    async def get(self, request):
        res = {'aid': None}
        token = request.headers.get('x-rfp-token')
        if token is None:
            raise HTTPException(403)
        acc = await check_token(request.app.config, token)
        if acc is None:
            res['message'] = await fix_bad_token(request.app.config)
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT a.id, a.user_id, a.requested,
                      a.swap, a.swexpire, u.username, u.last_visit
                 FROM accounts AS a, users AS u
                 WHERE a.id = $1 AND a.user_id = u.id''', acc.get('aid'))
        await conn.close()
        if acc is None or acc.get('user_id') is None \
                or acc.get('last_visit') > acc.get('requested') \
                or (acc.get('swap')
                    and acc.get('swexpire') > datetime.now(UTC)):
            res['message'] = 'Действие невозможно, брелок под сомнением.'
            return JSONResponse(res)
        res['aid'] = True
        res['username'] = acc.get('username')
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': False}
        d = await request.form()
        address, cache, captcha = (
            d.get('address'), d.get('cache'), d.get('captcha'))
        if not all((address, cache, captcha)):
            res['message'] = 'Данные не соответствуют запросу.'
            return JSONResponse(res)
        suffix, val = await extract_cache(request, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        message, acc = await check_acc(request, conn, address)
        if message:
            res['message'] = message
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            await conn.close()
            return JSONResponse(res)
        res['done'] = True
        asyncio.ensure_future(
            change_pattern(request.app.config, suffix))
        if acc:
            await conn.execute(
                '''UPDATE accounts SET requested = $1, swap = null
                     WHERE id = $2''', datetime.now(UTC), acc.get('id'))
            asyncio.ensure_future(
                send_rfp_mail(request, acc))
            await set_flashed(
                request, 'Вам выслано письмо с инструкциями, следуйте им...')
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        address, passwd, confirma = (
            d.get('address'), d.get('passwd'), d.get('confirma'))
        if not all((address, passwd, confirma)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if passwd != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        acc = await check_token(request.app.config, d.get('key'))
        if acc is None:
            res['message'] = 'Брелок недействителен.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT a.id, a.address, a.user_id, u.username
                 FROM accounts AS a, users AS u
                 WHERE a.user_id = u.id AND a.id = $1''', acc.get('aid'))
        if acc is None or acc.get('address') != address or \
                acc.get('user_id') is None:
            res['message'] = 'Действие невозможно, неверный запрос.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            '''UPDATE users SET password_hash = $1, last_visit = $2
                 WHERE id = $3''',
            pbkdf2_sha256.hash(passwd), datetime.now(UTC), acc.get('user_id'))
        res['done'] = True
        await conn.close()
        await set_flashed(
            request, f'Внимание, {acc.get("username")}, у Вас новый пароль.')
        return JSONResponse(res)


class LogoutE(HTTPEndpoint):
    async def delete(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                cache = cache.get('cache')
                conn = await get_conn(request.app.config)
                u = await conn.fetchrow(
                    '''SELECT u.id, u.username, s.suffix, s.brkey
                         FROM users AS u, sessions AS s
                         WHERE s.user_id = u.id
                           AND s.suffix = $1''', cache)
                if u and u.get('suffix') == ses and u.get('brkey') == brkey:
                    if request.session.get('_uid'):
                        request.session.pop('_uid')
                    await conn.execute(
                        'DELETE FROM sessions WHERE user_id = $1',
                        u.get('id'))
                    await set_flashed( request, f'Пока, {u.get("username")}!')
                    res['result'] = True
                await conn.close()
        return JSONResponse(res)


class Logout(HTTPEndpoint):
    async def delete(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                cache = cache.get('cache')
                conn = await get_conn(request.app.config)
                u = await conn.fetchrow(
                    '''SELECT u.username, s.suffix, s.brkey
                         FROM users AS u, sessions AS s
                         WHERE s.user_id = u.id
                           AND s.suffix = $1''', cache)
                if u and u.get('suffix') == ses and u.get('brkey') == brkey:
                    if request.session.get('_uid'):
                        request.session.pop('_uid')
                    await conn.execute(
                        'DELETE FROM sessions WHERE suffix = $1', cache)
                    await set_flashed(request, f'Пока, {u.get("username")}!')
                    res['result'] = True
                await conn.close()
        return JSONResponse(res)


class Login(HTTPEndpoint):
    async def post(self, request):
        d = await request.form()
        res = {'token': None}
        brkey = request.headers.get('x-br-tee', None)
        if not brkey:
            res['message'] = 'Упс..!'
            return JSONResponse(res)
        login, passwd, rme, cache, captcha = (
            d.get('login'), d.get('passwd'),
            int(d.get('rme')), d.get('cache'),
            d.get('captcha'))
        if not cache:
            res['message'] = BADCAPTCHA
            return JSONResponse(res)
        suffix, val = await extract_cache(request, cache)
        if captcha != val:
            print('yep')
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        user = await filter_user(conn, login)
        if user and pbkdf2_sha256.verify(
                passwd, user.get('password_hash')):
            d, now = await create_session(
                request.app.config, conn, rme, user, brkey)
            request.session['_uid'] = d
            res['token'] = await create_login_token(request, rme, d, now)
            await set_flashed(request, f'Привет, {user.get("username")}!')
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            asyncio.ensure_future(
                rem_old_session(request.app.config, user.get('id')))
        else:
            res['message'] = 'Неверный логин или пароль, вход невозможен.'
        await conn.close()
        return JSONResponse(res)
