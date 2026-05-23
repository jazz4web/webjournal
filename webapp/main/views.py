import asyncio
import functools
import os
import random

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, PlainTextResponse, Response

from ..dirs import images
from ..errors import E404

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..common.random import randomize, samples
from .tools import resize


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
                 'listed': False})
        if realm == 'rfp':
            await conn.close()
            return request.app.jinja.TemplateResponse(
                request, 'main/rfp.html',
                {'listed': False})
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
