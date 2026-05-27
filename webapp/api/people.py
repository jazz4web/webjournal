from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.pg import get_conn
from .pg import check_rel, filter_target_user
from .tools import check_g_secure, check_profile_permissions


class Profile(HTTPEndpoint):
    async def get(self, request):
        res = {'user': None, 'cu': None}
        token = request.headers.get('x-auth-sestee')
        username = request.query_params.get('username')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, token)
        res['cu'] = cu
        message = await check_g_secure(request, cu, 0)
        if message:
            res['message'] = message
            await conn.close()
            return JSONResponse(res)
        if cu and username:
            target = await filter_target_user(request, conn, username)
            if target is None:
                res['message'] = f'{username}? Не знаем такого...'
                await conn.close()
                return JSONResponse(res)
            res['user'] = target
            rel = await check_rel(conn, cu.get('id'), target.get('uid'))
            await check_profile_permissions(cu, target, res, rel)
            if res['address']:
                res['user']['address'] = await conn.fetchval(
                    'SELECT address FROM accounts WHERE user_id = $1',
                    target.get('uid'))
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)
