from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_profile(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'people/profile.html',
        {'cu': cu,
         'listed': True,
         'username': request.path_params.get('username'),
         'interval': request.app.config.get('RINTERVAL', cast=float),
         'flashed': await get_flashed(request)})
