import asyncio
import functools
import os
import random

from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, PlainTextResponse, RedirectResponse, Response)

from ..dirs import images
from ..errors import E404

from ..api.tasks import check_swapped
from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..common.random import randomize, samples
from .tools import resize


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
    await conn.close()
    raise HTTPException(status_code=404, detail='Такой страницы у нас нет.')


async def show_avatar(request):
    size = request.path_params.get('size')
    if size < 22 or size > 160:
        raise HTTPException(status_code=404, detail=E404)
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT id, username FROM users WHERE username = $1',
        request.path_params.get('username'))
    if res is None:
        await conn.close()
        raise HTTPException(status_code=404, detail=E404)
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
    if cu and realm == 'logout':
        out = 1
    if cu and realm == 'logoute':
        oute = 1
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'main/index.html',
        {'listed': True,
         'cu': cu,
         'out': out,
         'oute': oute,
         'flashed': await get_flashed(request)})
