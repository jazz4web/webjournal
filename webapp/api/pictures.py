from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..pictures.attri import status
from .pg import (
    check_last, create_new_album, get_album, get_user_stat,
    rem_session, select_albums)
from .tools import check_g_secure, check_permissions, check_secure


class Albumstat(HTTPEndpoint):
    async def get(self, request):
        res = {'album': None}
        token = request.headers.get('x-auth-sestee')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        message = await check_g_secure(request, cu, 150)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        suffix = request.query_params.get('suffix', None)
        if suffix is None:
            res['message'] = 'Не указан альбом.'
            await conn.close()
            return JSONResponse(res)
        album = await get_album(conn, cu.get('id'), suffix)
        await conn.close()
        if album is None:
            res['message'] = 'Альбом не существует.'
            return JSONResponse(res)
        res['album'] = album
        return JSONResponse(res)


class Albums(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 150)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM albums WHERE author_id = $1', cu.get('id'))
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = await select_albums(
            conn, cu.get('id'), page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        res['extra'] = res['pagination'] is None or \
                (res['pagination'] and res['pagination']['page'] == 1)
        res['stat'] = await get_user_stat(conn, cu.get('id'))
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        title, state = d.get('title', ''), d.get('state')
        if not title or len(title) > 100 or \
                d.get('state') not in status:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        ses, brkey, message = await check_secure(request)
        if message:
            res['message'] = message
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if message := await check_permissions(cu, 150):
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if brkey != cu.get('brkey') or ses != cu.get('ses'):
            res['message'] = await rem_session(conn, cu)
            await conn.close()
            return JSONResponse(res)
        rep = await conn.fetchval(
            '''SELECT suffix FROM albums
                 WHERE title = $1 AND author_id = $2''',
            title.strip(), cu.get('id'))
        if rep:
            res['message'] = 'Альбом с таким именем уже есть.'
            await conn.close()
            return JSONResponse(res)
        new = await create_new_album(
            conn, cu.get('id'), title.strip(), state.strip())
        res['done'] = True
        res['target'] = request.url_for('pictures:album', suffix=new)._url
        await conn.close()
        await set_flashed(request, 'Альбом создан.')
        return JSONResponse(res)
