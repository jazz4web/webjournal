from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..main.pg import get_counters


async def show_lcarts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/lcarts.html',
        {'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_carts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/carts.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_cart(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/cart.html',
        {'cu': cu,
         'slug': request.path_params.get('slug'),
         'listed': False,
         'flashed': await get_flashed(request)})


async def show_lfollowed(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/llenta.html',
        {'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'listed': True,
         'counters': counters,
         'flashed': await get_flashed(request)})


async def show_followed(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/lenta.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'counters': counters,
         'flashed': await get_flashed(request)})


async def show_art(request):
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/art.html',
        {'cu': cu,
         'slug': slug,
         'listed': False,
         'counters': counters,
         'flashed': await get_flashed(request)})


async def show_arts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/arts.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'counters': counters,
         'flashed': await get_flashed(request)})


async def show_larts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'arts/labeled-arts.html',
        {'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'listed': True,
         'counters': counters,
         'flashed': await get_flashed(request)})
