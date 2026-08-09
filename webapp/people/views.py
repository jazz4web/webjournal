import asyncio

from ..api.tasks import check_swapped
from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..main.pg import get_counters


async def show_people(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'people/people.html',
        {'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'counters': counters,
         'flashed': await get_flashed(request)})


async def show_profile(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    username = request.path_params.get('username')
    if cu and cu.get('username') == username:
        asyncio.ensure_future(
            check_swapped(request.app.config))
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'people/profile.html',
        {'cu': cu,
         'listed': True,
         'username': username,
         'interval': request.app.config.get('RINTERVAL', cast=float),
         'counters': counters,
         'flashed': await get_flashed(request)})
