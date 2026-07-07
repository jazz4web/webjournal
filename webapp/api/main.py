from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.pg import get_conn
from .redi import assign_cache


class Index(HTTPEndpoint):
    async def post(self, request):
        res = {'redirect': None}
        conn = await get_conn(request.app.config)
        ses = request.session.get('_uid')
        cu = await checkcu(
            request, conn, (await request.form()).get('auth'))
        if ses and cu is None:
            res['redirect'] = True
        await conn.close()
        return JSONResponse(res)


class Captcha(HTTPEndpoint):
    async def get(self, request):
        if request.headers.get('x-br-s') is None:
            raise HTTPException(403)
        conn = await get_conn(request.app.config)
        captcha = await conn.fetchrow(
            'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1')
        res = await assign_cache(
            request, 'captcha:',
            captcha.get('suffix'), captcha.get('val'), 180)
        url = request.url_for('captcha', suffix=captcha.get('suffix'))._url
        await conn.close()
        return JSONResponse({'captcha': res, 'url': url})
