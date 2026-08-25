import asyncio
import functools
import os
import random

from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, PlainTextResponse, RedirectResponse, Response)

from ..dirs import images

from ..api.parse import LABELS
from ..api.tasks import check_swapped
from ..api.pg import check_last
from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..common.random import randomize, samples
from ..drafts.attri import status as statusd
from ..pictures.attri import status
from .pg import check_state, check_topic, get_counters
from .tools import resize


async def show_public(request):
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    if cu:
        return RedirectResponse(request.url_for('arts:art', slug=slug), 301)
    topic = dict()
    await check_topic(request, conn, slug, topic)
    counters = await get_counters(conn, cu)
    await conn.close()
    if not topic:
        raise HTTPException(404)
    return request.app.jinja.TemplateResponse(
        request, 'main/show-public.html',
        {'topic': topic,
         'slug': slug,
         'counters': counters,
         'listed': False})


async def show_robots(request):
    conn = await get_conn(request.app.config)
    text = await conn.fetchval('SELECT robots FROM settings') or \
            request.app.jinja.get_template(
                'main/robots.txt').render(request=request)
    await conn.close()
    return PlainTextResponse(text)


async def show_sitemap_t(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    if cu is None or cu.get('weight') < 250:
        await conn.close()
        raise HTTPException(404)
    page = await parse_page(request)
    last = await check_last(
        conn, page,
        request.app.config.get('UNDEFINED', cast=int, default=30),
        'SELECT count(*) FROM articles WHERE state = $1',
        statusd.pub)
    if page > last:
        page = last
    per_page = request.app.config.get('UDEFINED', cast=int, default=30)
    arts = [request.url_for('public', slug=art.get('slug'))._url for art
            in await conn.fetch(
                '''SELECT slug FROM articles
                     WHERE state = $1 ORDER BY published DESC
                     LIMIT $2 OFFSET $3''',
                statusd.pub, per_page, per_page*(page-1))]
    arts.append(f'page={page}, last page={last}')
    await conn.close()
    return PlainTextResponse('\n'.join(arts))


async def show_sitemap(request):
    conn = await get_conn(request.app.config)
    arts = await conn.fetch(
        '''SELECT slug, published, edited FROM articles
             WHERE state = $1 ORDER BY published DESC LIMIT 250''',
        statusd.pub)
    await conn.close()
    response = request.app.jinja.TemplateResponse(
        request, 'main/sitemap.xml',
        {'arts': arts})
    response.media_type = 'applictation/xml'
    response.headers['content-type'] = 'application/xml'
    return response


async def show_picture(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    target = await conn.fetchrow(
        '''SELECT albums.state, albums.author_id, pictures.suffix,
                  pictures.picture, pictures.format FROM albums, pictures
             WHERE pictures.suffix = $1
               AND albums.id = pictures.album_id''',
        request.path_params.get('suffix'))
    if target is None:
        response = FileResponse(
            os.path.join(images, '404.png'))
        response.headers.append(
            'cache-control',
            'max-age=0, no-store, no-cache, must-revalidate')
    else:
        if await check_state(conn, target, cu):
            response = Response(
                target.get('picture'),
                media_type=f'image/{target.get("format").lower()}')
            response.headers.append(
                'cache-control',
                'public, max-age={0}'.format(
                    request.app.config.get(
                        'FILE_MAX_AGE', cast=int, default=0)))
        else:
            if target['state'] == status.ffo:
                picname = '403a.png'
            else:
                picname = '403.png'
            response = FileResponse(
                os.path.join(images, picname))
            response.headers.append(
                'cache-control',
                'max-age=0, no-store, no-cache, must-revalidate')
    await conn.close()
    return response


async def jump(request):
    suffix = request.path_params.get('suffix')
    conn = await get_conn(request.app.config)
    if len(suffix) in (6, 7, 9, 10):
        alias = await conn.fetchrow(
            'SELECT url, clicked, author_id FROM aliases WHERE suffix = $1',
            suffix)
        if alias and alias.get('author_id'):
            cu = await getcu(request, conn)
            jumps = request.session.get('jumps', list())
            if suffix not in jumps and \
                    (not cu or cu.get('id') != alias.get('author_id')):
                clicked = alias.get('clicked') + 1
                if clicked > 99999:
                    clicked = 9
                await conn.execute(
                    'UPDATE aliases SET clicked = $1 WHERE suffix = $2',
                    clicked, suffix)
                jumps.append(suffix)
                if len(jumps) > 20:
                    del jumps[0]
                request.session['jumps'] = jumps
            await conn.close()
            return RedirectResponse(alias.get('url'), 301)
    elif len(suffix) in (8, 11, 12, 13):
        art = await conn.fetchrow(
            'SELECT suffix, slug FROM articles WHERE suffix = $1', suffix)
        await conn.close()
        if art:
            curl = request.url_for('public', slug=art.get('slug'))
            rurl = request.url_for('arts:art', slug=art.get('slug'))
            response = RedirectResponse(rurl, 301)
            response.headers.append('Link', f'<{curl}>; rel="canonical"')
            return response
    await conn.close()
    raise HTTPException(404)


async def show_avatar(request):
    size = request.path_params.get('size')
    if size < 22 or size > 160:
        raise HTTPException(404)
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT id, username FROM users WHERE username = $1',
        request.path_params.get('username'))
    if res is None:
        await conn.close()
        raise HTTPException(404)
    ava = await conn.fetchval(
        'SELECT picture FROM avatars WHERE user_id = $1', res.get('id'))
    await conn.close()
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(
        None, functools.partial(resize, size, ava))
    response = Response(image, media_type='image/png')
    if ava is None:
        response.headers.append('cache-control', 'public, max-age=0')
    else:
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'FILE_MAX_AGE', cast=int, default=0)))
    return response


async def show_humans(request):
    text = request.app.jinja.get_template(
        'main/humans.txt').render(request=request)
    return PlainTextResponse(text)


async def show_favicon(request):
    if request.method == 'GET':
        response = FileResponse(
            os.path.join(images, 'favicon.ico'))
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'FILE_MAX_AGE', cast=int, default=0)))
        return response


async def show_index(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    realm = request.query_params.get('realm')
    if cu is None:
        if realm == 'login':
            await conn.close()
            return request.app.jinja.TemplateResponse(
                request, 'main/login.html',
                {'item': random.choice(samples),
                 'value': await randomize(7),
                 'flashed': await get_flashed(request),
                 'listed': False})
        if realm == 'rfp':
            await conn.close()
            return request.app.jinja.TemplateResponse(
                request, 'main/rfp.html',
                {'listed': False})
        if realm == 'reg':
            asyncio.ensure_future(
                check_swapped(request.app.config))
            await conn.close()
            return request.app.jinja.TemplateResponse(
                request, 'main/reg.html',
                {'perm': request.app.config.get('REGPERM', cast=bool),
                 'listed': False})
    out, oute = 0, 0
    art = await conn.fetchval('SELECT indexpage FROM settings')
    if art:
        art = await conn.fetchrow(
            '''SELECT a.id, a.suffix, a.title,
                      a.html, a.edited, u.username
                 FROM articles AS a, users AS u
                 WHERE a.author_id = u.id AND a.suffix = $1''', art)
        if art:
            art = {'id': art.get('id'),
                   'suffix': art.get('suffix'),
                   'title': art.get('title'),
                   'html': art.get('html'),
                   'edited': art.get('edited').isoformat(),
                   'kws': [label.get('label') for label in await conn.fetch(
                       LABELS, art.get('id'))],
                   'author': art.get('username')}
    if cu and realm == 'logout':
        out = 1
    if cu and realm == 'logoute':
        oute = 1
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'main/index.html',
        {'listed': True,
         'cu': cu,
         'out': out,
         'oute': oute,
         'art': art,
         'counters': counters,
         'flashed': await get_flashed(request)})
