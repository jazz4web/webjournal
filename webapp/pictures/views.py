from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from .attri import status


async def show_album(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'pictures/album.html',
        {'cu': cu,
         'listed': True,
         'status': status,
         'suffix': request.path_params.get('suffix'),
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_albums(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'pictures/albums.html',
        {'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'status': status,
         'flashed': await get_flashed(request)})
