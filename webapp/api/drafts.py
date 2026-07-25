import re

from datetime import datetime, UTC

from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from ..auth.attri import groups
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import (
    change_draft, check_draft, check_last, create_d,
    insert_par, edit_par, rem_session, remove_par,
    save_par, select_drafts, select_labeled_drafts, undress_art_links)
from .tools import check_g_secure, check_permissions, check_secure


class Paragraph(HTTPEndpoint):
    async def delete(self, request):
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
        slug, num = d.get('slug', ''), d.get('num', None)
        if not all((slug, num)):
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
        if await conn.fetchval(
                '''SELECT num FROM paragraphs
                     WHERE article_id = $1 AND num = $2''',
                draft, int(num)) is not None:
            res['html'] = await remove_par(conn, draft, int(num))
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            draft)
        res['done'] = True
        await conn.close()
        return JSONResponse(res)

    async def get(self, request):
        res = {'text': None}
        slug = request.query_params.get('slug', '')
        num = request.query_params.get('num', None)
        token = request.headers.get('x-auth-sestee')
        if not slug or num is None or token is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        message = await check_g_secure(request, cu, 100)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        text = await conn.fetchval(
            '''SELECT par.mdtext FROM paragraphs AS par, articles AS arts
                 WHERE par.num = $1
                   AND arts.author_id = $2
                   AND arts.slug = $3
                   AND par.article_id = arts.id''',
            int(num), cu.get('id'), slug)
        await conn.close()
        if text is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        res['text'] = text
        return JSONResponse(res)

    async def post(self, request):
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
        slug, text, code = (
            d.get('slug', ''), d.get('text', ''), int(d.get('code', '0')))
        if not slug or not text:
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
        res['html'] = await save_par(conn, draft, text, code)
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            draft)
        res['done'] = True
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
        slug, num, insert, text, code = (
            d.get('slug', ''), d.get('num', None), d.get('insert', None),
            d.get('text', ''), d.get('code', None))
        if not all((slug, num, insert, text, code)):
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
        last = await conn.fetchval(
            '''SELECT num FROM paragraphs
                 WHERE article_id = $1 ORDER BY num DESC''', draft)
        if int(num) > last:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if int(insert):
            res['html'] = await insert_par(
                conn, draft, text.strip(), int(num), int(code))
        else:
            res['html'] = await edit_par(
                conn, draft, text.strip(), int(num), int(code))
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            draft)
        await conn.close()
        res['done'] = True
        return JSONResponse(res)


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

    async def patch(self, request):
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
        draft = await conn.fetchrow(
            'SELECT id, author_id FROM articles WHERE slug = $1',
            d.get('slug', ''))
        if draft is None:
            res['message'] = 'Ничего не нашлось по запросу.'
            await conn.close()
            return JSONResponse(res)
        if (cu.get('id') == draft.get('author_id') and
            cu. get('weight') < 200) or \
                    (cu.get('id') != draft.get('author_id') and
                     cu.get('group') != groups.root):
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        res['done'] = True
        await undress_art_links(conn, draft.get('id'))
        await set_flashed(request, 'Атрибут у ссылок удалён.')
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
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
        value, slug = d.get('value', ''), d.get('slug', '')
        if not all((value, slug)) or value not in status:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        draft = await conn.fetchrow(
            '''SELECT id, meta, summary
                 FROM articles WHERE slug = $1 AND author_id = $2''',
            d.get('slug'), cu.get('id'))
        if draft is None:
            res['message'] = 'Черновик не существует.'
            await conn.close()
            return JSONResponse(res)
        if draft.get('summary') is None:
            res['message'] = 'Сначала отредактируйте аннотацию.'
            await conn.close()
            return JSONResponse(res)
        if value == status.pub and draft.get('meta') is None:
            res['message'] = 'Напишите описание для поисковиков.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            'UPDATE articles SET state = $1 WHERE id = $2',
            value, draft.get('id'))
        published = await conn.fetchrow(
            'SELECT published, author_id FROM articles WHERE id = $1',
            draft.get('id'))
        if published.get('published') is None and \
                value in (status.pub, status.priv, status.ffo):
            now = datetime.now(UTC)
            await conn.execute(
                '''UPDATE articles SET published = $1, edited = $1
                     WHERE id = $2''', now, draft.get('id'))
            await conn.execute(
                'UPDATE users SET last_published = $1 WHERE id = $2',
                now, published.get('author_id'))
        res['done'] = True
        await set_flashed(request, f'Статус черновика изменён на "{value}".')
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
        if field not in ('commented', 'meta', 'summary', 'title'):
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
