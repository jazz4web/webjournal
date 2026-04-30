from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException


class Captcha(HTTPEndpoint):
    async def post(self, request):
        raise HTTPException(403, 'Доступ ограничен, недостаточно прав.')
