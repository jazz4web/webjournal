import os

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, PlainTextResponse

from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_log(request):
    l = request.path_params.get('log')
    if l not in ('access.log', 'previous.log'):
        raise HTTPException(404)
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    if cu and cu.get('weight') in (250, 255):
        if l == 'access.log':
            l = f'/var/log/nginx/{l}'
        else:
            l = '/var/log/nginx/access.log.1'
        if os.path.exists(l):
            response = FileResoponse(l)
        else:
            a = 'Файл не существует.\n'
            m = 'Убедитесь, что вы используете Nginx.'
            response = PlainTextResponse(a + m)
        return response
    raise HTTPException(404)


async def admin_au_pic(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/auth-pictures.html',
        {'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'author': request.path_params.get('username'),
         'flashed': await get_flashed(request)})


async def admin_album(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/album.html',
        {'cu': cu,
         'listed': True,
         'album': request.path_params.get('album'),
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def admin_pictures(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/pictures.html',
        {'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})


async def admin_auth_aliases(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/auth-aliases.html',
        {'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'author': request.path_params.get('username'),
         'flashed': await get_flashed(request)})


async def admin_aliases(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/aliases.html',
        {'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_tools(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/tools.html',
        {'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})
