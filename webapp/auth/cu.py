import asyncio

from ..api.tasks import ping_user
from ..api.tokens import check_token
from ..common.flashed import set_flashed

session = '''SELECT u.id, u.username, u.registered, u.last_published,
                    u.ugroup, u.weight, s.brkey, s.suffix
               FROM users AS u, sessions AS s
               WHERE u.id = s.user_id AND s.suffix = $1'''
old = 'DELETE FROM sessions WHERE suffix = $1'


async def checkcu(request, conn, token):
    cache = await check_token(request.app.config, token)
    if cache:
        cache = cache.get('cache')
        query = await conn.fetchrow(session, cache)
        if query and not query.get('weight'):
            if request.session.get('_uid'):
                request.sesstion.pop('_uid')
            await conn.execute(old, cache)
            await set_flashed(request, 'Ваша сессия аннулирована.')
            return None
        if query:
            asyncio.ensure_future(
                ping_user(request.app.config, query.get('id')))
            return {'id': query.get('id'),
                    'username': query.get('username'),
                    'group': query.get('ugroup'),
                    'registered': query.get('registered'),
                    'lp': query.get('last_published'),
                    'weight': query.get('weight'),
                    'brkey': query.get('brkey'),
                    'ava': request.url_for(
                        'ava', username=query.get('username'), size=22)._url,
                    'ses': query.get('suffix')}
    else:
        if s := request.session.get('_uid'):
            request.session.pop('_uid')
            await conn.execute(old, s)
    return None


async def getcu(request, conn):
    if cache := request.session.get('_uid'):
        query = await conn.fetchrow(session, cache)
        if query and not query.get('weight'):
            request.session.pop('_uid')
            await conn.execute(old, cache)
            await set_flashed(request, 'Ваша сессия аннулирована.')
            return None
        if query:
            asyncio.ensure_future(
                ping_user(request.app.config, query.get('id')))
            return {'id': query.get('id'),
                    'username': query.get('username'),
                    'lp': query.get("last_published"),
                    'weight': query.get('weight'),
                    'ava': request.url_for(
                        'ava', username=query.get('username'), size=22)._url,
                    'ses': query.get('suffix')}
        else:
            request.session.pop('_uid')
    return None
