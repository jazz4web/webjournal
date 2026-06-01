from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_tools(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'admin/tools.html',
        {'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})
