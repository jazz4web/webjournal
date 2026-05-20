import asyncio

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .redi import extract_cache
from .pg import create_session, filter_user
from .tasks import change_pattern, rem_old_session
from .tokens import check_token, create_login_token
from .tools import check_secure

BADCAPTCHA = 'Неверный код, повторите попытку.'


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
