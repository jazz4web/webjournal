from starlette.exceptions import HTTPException

from ..common.pg import get_conn
from .cu import getcu


async def reset_fp(request):
    key = request.path_params.get('token')
    if len(key) < 100:
        raise HTTPException(404)
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    view = request['path'].split('/')[2]
    template = f'auth/{view}.html'
    return request.app.jinja.TemplateResponse(
        request, template,
        {'key': key,
         'cu': cu,
         'interval': request.app.config.get(
             'RINTERVAL', cast=float),
         'listed': False})
