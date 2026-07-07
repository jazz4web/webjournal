from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from .attri import status


async def show_drafts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'drafts/drafts.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_draft(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        request, 'drafts/draft.html',
        {'cu': cu,
         'slug': request.path_params.get('slug'),
         'listed': False,
         'status': status,
         'flashed': await get_flashed(request)})


async def show_dlabeled(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        request, 'drafts/labeled.html',
        {'cu': cu,
         'label': request.path_params.get('label'),
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})
