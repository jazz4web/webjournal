from datetime import datetime, timedelta, UTC

from jwt import decode as jwtdecode, encode as jwtencode, PyJWTError


async def create_request_token(request, aid):
    delta = timedelta(
        seconds=round(
            3600*request.app.config.get('TLENGTH', cast=float)))
    cache = {'aid': aid, 'exp': datetime.now(UTC) + delta}
    return jwtencode(
        cache, request.app.config.get('SECRET_KEY'), algorithm='HS256')


async def check_token(config, token):
    try:
        cache = jwtdecode(
            token, config.get('SECRET_KEY'), algorithms=['HS256'])
        pass
    except PyJWTError:
        return None
    return cache


async def create_login_token(request, rme, cache, now):
    if rme:
        delta = timedelta(
            seconds=request.app.config.get('SESSION_LIFETIME', cast=int))
    else:
        delta = timedelta(seconds=2*60*60)
    d = {'cache': cache, 'exp': now + delta}
    return jwtencode(
        d, request.app.config.get('SECRET_KEY'), algorithm='HS256')
