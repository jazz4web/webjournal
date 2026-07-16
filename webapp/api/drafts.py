import re

from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import (
    change_draft, check_draft, check_last, create_d,
    rem_session, select_drafts, select_labeled_drafts)
from .tools import check_g_secure, check_permissions, check_secure


class Labels(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        if token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 100)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = $1
                   AND articles.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND articles.state IN ($3, $4)''',
            cu.get('id'), request.query_params.get('label'),
            status.draft, status.cens)
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_labeled_drafts(
            request, conn, cu.get('id'), request.query_params.get('label'),
            res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'labels': None}
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
        slug, labels = d.get('slug', ''), d.get('labels', '').rstrip(',')
        if not slug:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        draft = await conn.fetchval(
            'SELECT id FROM articles WHERE slug = $1 AND author_id = $2',
            slug, cu.get('id'))
        if draft is None:
            res['message'] = 'Черновик не обнаружен.'
            await conn.close()
            return JSONResponse(res)
        cur = [label.get('label') for label in await conn.fetch(
            '''SELECT labels.label FROM articles, labels, als
                 WHERE articles.id = als.article_id
                   AND labels.id = als.label_id
                   AND articles.id = $1''', draft)]
        new = [l.strip().lower() for l in labels.split(', ') if l]
        for each in new:
            if not re.match(r'^[a-zа-яё\d\-]{1,32}$', each):
                res['message'] = 'Запрос содержит неверные параметры.'
                await conn.close()
                return JSONResponse(res)
        lq = 'SELECT id FROM labels WHERE label = $1'
        for each in cur:
            if each not in new:
                lid = await conn.fetchval(lq, each)
                await conn.execute(
                    '''DELETE FROM als WHERE article_id = $1
                         AND label_id = $2''', draft, lid)
        for each in new:
            if each not in cur:
                lid = await conn.fetchval(lq, each)
                if lid is None:
                    await conn.execute(
                        'INSERT INTO labels (label) VALUES ($1)', each)
                    lid = await conn.fetchval(lq, each)
                await conn.execute(
                    '''INSERT INTO als (article_id, label_id)
                         VALUES ($1, $2)''', draft, lid)
        res['labels'] = True
        await conn.close()
        await set_flashed(request, 'Метки установлены.')
        return JSONResponse(res)


class Draft(HTTPEndpoint):
    async def get(self, request):
        res = {'draft': None}
        token = request.headers.get('x-auth-sestee')
        if token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 0)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        slug = request.query_params.get('slug', '')
        target = dict()
        await check_draft(request, conn, slug, cu.get('id'), target)
        if not target:
            res['message'] = 'Ничего не найдено по запросу.'
            await conn.close()
            return JSONResponse(res)
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            target.get('id'))
        res['chstate'] = True if target['html'] \
                and target['state'] != status.cens else False
        res['cens'] = target['state'] == status.cens
        res['keeper'] = cu.get('weight') >= 200
        res['draft'] = target
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
        field, value, slug = (
            d.get('field', ''), d.get('value', ''), d.get('slug', ''))
        if not all((field, value, slug)):
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if field not in ('meta', 'summary'):
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        draft = await conn.fetchval(
            'SELECT id FROM articles WHERE slug = $1 AND author_id = $2',
            d.get('slug', ''), cu.get('id'))
        if draft is None:
            res['message'] = 'Черновик не существует.'
            await conn.close()
            return JSONResponse(res)
        s = await change_draft(request, conn, draft, field, value)
        res['done'] = True
        if s:
            res['slug'] = s
        await set_flashed(request, 'Изменено успешно.')
        await conn.close()
        return JSONResponse(res)


class Drafts(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        token = request.headers.get('x-auth-sestee')
        if token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 0)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=5),
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3)''',
            cu.get('id'), status.draft, status.cens)
        if page > last:
            res['message'] = f'Всего известно страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_drafts(
            request, conn, cu.get('id'), res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=5), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        res['extra'] = not res['pagination'] or \
                (res['pagination'] and res['pagination']['page'] == 1)
        res['canwrite'] = cu.get('weight') >= 100
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        title = d.get('title', '')
        if not title or len(title.strip()) > 100:
            res['message'] = 'Запрос содержит неверные параметры, отменено.'
            return JSONResponse(res)
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
        slug = await create_d(conn, title.strip(), cu.get('id'))
        await conn.close()
        res['draft'] = request.url_for('drafts:draft', slug=slug)._url
        await set_flashed(request, 'Черновик создан, можно спокойно работать.')
        return JSONResponse(res)
