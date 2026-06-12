from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


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
