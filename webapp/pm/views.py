from starlette.exceptions import HTTPException

from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_conversation(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    username = request.path_params.get('username')
    if username == cu.get('username'):
        raise HTTPException(404)
    return request.app.jinja.TemplateResponse(
        request, 'pm/conversation.html',
        {'cu': cu,
         'username': username,
         'page': await parse_page(request),
         'nopage': request.query_params.get('page', '0'),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_conversations(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        request, 'pm/conversations.html',
        {'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})
