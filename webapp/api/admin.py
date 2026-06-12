import asyncio
import re

from datetime import datetime, UTC

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.attri import groups, USERNAME_PATTERN
from ..auth.cu import checkcu
from ..auth.pg import check_username, create_user
from ..common.aparsers import parse_page, parse_url
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_last, rem_session, sadmin_auth_aliases
from .tools import check_permissions, check_g_secure, check_secure


class AuthAlis(HTTPEndpoint):
    async def delete(self, request):
        res = {'done': None}
        d = await request.form()
        suffix, page, url = (
            d.get('suffix', ''),
            int(d.get('page', '0')),
            d.get('endpoint', ''))
        if page >= 2:
            url += f'?page={page}'
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 250):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        alias = await conn.fetchrow(
            '''SELECT a.suffix, u.weight, u.username
                 FROM aliases AS a, users AS u
                   WHERE a.author_id = u.id
                     AND a.suffix = $1''', suffix)
        if alias is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') <= alias.get('weight'):
            res['message'] = 'У вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            'DELETE FROM aliases WHERE suffix = $1', suffix)
        await conn.close()
        await set_flashed(request, 'Алиас успешно удалён.')
        res['done'] = True
        res['url'] = url
        return JSONResponse(res)

    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 250)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        author = await conn.fetchrow(
            'SELECT id, username, weight FROM users WHERE username = $1',
            request.query_params.get('author', '1empty'))
        if author is None:
            res['message'] = 'Ничего не найдено по запросу.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ALIASES_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM aliases WHERE author_id = $1',
            author.get('id'))
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await sadmin_auth_aliases(
            request, conn, author, cu, res['pagination'], page,
            request.app.config.get('ALIASES_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination'] and \
                (res['pagination']['next'] or res['pagination']['prev']):
            res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Alis(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        await conn.close()
        res['cu'] = cu
        message = await check_g_secure(request, cu, 250)
        if message:
            res['message'] = message
        return JSONResponse(res)

    async def post(self, request):
        res = {'alias': None}
        d = await request.form()
        link = d.get('link') or 'empty'
        if '/' in link:
            link = link.split('/')[-1]
        if len(link) not in (6, 7, 9, 10):
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 250):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            '''SELECT a.url, a.created, a.clicked, a.suffix,
                      u.weight, u.username FROM aliases AS a, users AS u
                 WHERE a.author_id = u.id
                   AND a.suffix = $1''', link)
        await conn.close()
        if target is None:
            res['message'] = 'Ничего не найдено по запросу.'
            return JSONResponse(res)
        res['alias'] = {'url': target.get('url'),
                        'parsed': await parse_url(target.get('url')),
                        'created': target.get('created').isoformat(),
                        'clicked': target.get('clicked'),
                        'canrem': target.get('weight') < cu.get('weight'),
                        'author': target.get('username'),
                        'profile': request.url_for(
                            'people:profile',
                            username=target.get('username'))._url,
                        'suffix': target.get('suffix'),
                        'alias': request.url_for(
                            'jump', suffix=target.get('suffix'))._url}
        return JSONResponse(res)

    async def put(self, request):
        res = {'redirect': None}
        d = await request.form()
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 250):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        author = await conn.fetchrow(
            'SELECT id, weight, username FROM users WHERE username = $1',
            d.get('username'))
        if author is None:
            res['message'] = 'Ничего не найдено по запросу.'
            await conn.close()
            return JSONResponse(res)
        howmany = await conn.fetchval(
            'SELECT count(*) FROM aliases WHERE author_id = $1',
            author.get('id'))
        await conn.close()
        if howmany:
            res['redirect'] = request.url_for(
                'admin:adauthal', username=author.get('username'))._url
        else:
            res['message'] = f'У {author.get("username")} нет ссылок.'
        return JSONResponse(res)


class DGroup(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        dgroup = d.get('dgroup', '')
        if dgroup not in groups.default_groups():
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
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
        await conn.execute('UPDATE settings SET dgroup = $1', dgroup)
        await conn.close()
        res['done'] = True
        await set_flashed(request, f'Группа по умолчанию &mdash; {dgroup}.')
        return JSONResponse(res)


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
        res['groups'] = groups.default_groups()
        res['dgroup'] = await conn.fetchval(
            'SELECT dgroup FROM settings') or groups.default_group()
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
