from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_lblog(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'blogs/labeled.html',
        {'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'username': request.path_params.get('username'),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_blogs(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'blogs/authors.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_blog(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'blogs/blog.html',
        {'cu': cu,
         'page': await parse_page(request),
         'username': request.path_params.get('username'),
         'listed': True,
         'flashed': await get_flashed(request)})
