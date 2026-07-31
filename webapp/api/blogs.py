from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_last, select_authored, select_authors


class Blog(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        if token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        username = request.query_params.get('username')
        author = await conn.fetchrow(
            'SELECT id, description FROM users WHERE username = $1', username)
        if author is None:
            res['message'] = f'Среди авторов {username} не найден.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3, $4)''',
            author.get('id'), status.pub, status.priv, status.ffo)
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_authored(
            request, conn, res['pagination'], author.get('id'), page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if author and author['description'] and res['pagination'] and \
                res['pagination']['page'] == 1:
            res['author'] = author.get('description')
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Authors(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        if token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('BLOGS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM users
                 WHERE last_published IS NOT NULL
                   AND description IS NOT NULL''')
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_authors(
            request, conn, res['pagination'],
            page, request.app.config('BLOGS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)
