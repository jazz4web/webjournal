import asyncio

from ..api.tasks import check_swapped
from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_profile(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    username = request.path_params.get('username')
    if cu and cu.get('username') == username:
        asyncio.ensure_future(
            check_swapped(request.app.config))
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'people/profile.html',
        {'cu': cu,
         'listed': True,
         'username': username,
         'interval': request.app.config.get('RINTERVAL', cast=float),
         'flashed': await get_flashed(request)})
