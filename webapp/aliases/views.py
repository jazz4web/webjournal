from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..main.pg import get_counters


async def show_aliases(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    counters = await get_counters(conn, cu)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'aliases/aliases.html',
        {'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'counters': counters,
         'flashed': await get_flashed(request)})
