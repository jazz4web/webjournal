from starlette.responses import JSONResponse

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn

E404 = 'Такой страницы у нас нет.'


async def show_error(request, exc):
    if exc.status_code == 403:
        exc.detail = 'Доступ ограничен, недостаточно прав.'
    if exc.status_code == 404:
        exc.detail = E404
    if exc.status_code == 405:
        exc.detail = 'Метод не позволен.'
    if request.method == 'GET':
        conn = await get_conn(request.app.config)
        cu = await getcu(request, conn)
        await conn.close()
        return request.app.jinja.TemplateResponse(
            request, 'errors/error.html',
            {'reason': exc.detail,
             'cu': cu,
             'flashed': await get_flashed(request),
             'error': exc.status_code},
            status_code=exc.status_code)
    else:
        res = JSONResponse(
            {'message': exc.detail, 'error': exc.status_code},
            status_code=exc.status_code)
        return res
