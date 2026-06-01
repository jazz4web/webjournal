import asyncio
import re

from datetime import datetime, UTC

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.attri import groups, USERNAME_PATTERN
from ..auth.cu import checkcu
from ..auth.pg import check_username, create_user
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import rem_session
from .tools import check_permissions, check_g_secure, check_secure


class Admin(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 255)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        username, address, password, confirma = (
            d.get('username'), d.get('address'),
            d.get('password'), d.get('confirma'))
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        if not all((username, address, password, confirma)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        if password != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 255):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        p = re.compile(USERNAME_PATTERN)
        if not p.match(username):
            res['message'] = 'Псевдоним не удовлетворяет требованиям сервиса.'
            await conn.close()
            return JSONResponse(res)
        if await check_username(request.app.config, username):
            res['message'] = f'Псевдоним {username} уже зарегистрирован.'
            await conn.close()
            return JSONResponse(res)
        acc = await conn.fetchval(
            'SELECT user_id FROM accounts WHERE address = $1', address)
        swapped = await conn.fetchval(
            'SELECT swap FROM accounts WHERE swap = $1 AND swexpire > $2',
            address, datetime.now(UTC))
        if acc or swapped:
            res['message'] = f'Адрес {address} уже используется.'
            await conn.close()
            return JSONResponse(res)
        dg = await conn.fetchval(
            'SELECT dgroup FROM settings') or groups.default_group()
        await conn.close()
        asyncio.ensure_future(
            create_user(request.app.config, username, address, password, dg))
        res['redirect'] = request.url_for(
            'people:profile', username=username)._url
        res['done'] = True
        await set_flashed(request, f'Аккаунт {username} успешно создан.')
        return JSONResponse(res)
