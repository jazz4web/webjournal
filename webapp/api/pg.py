import math

from datetime import datetime, timedelta, UTC

from validate_email import validate_email

from ..common.aparsers import iter_pages, parse_url
from ..common.random import get_unique_s


async def sadmin_auth_aliases(
        request, conn, author, cu, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT url, created, clicked, suffix FROM aliases
             WHERE author_id = $1
             ORDER BY created DESC LIMIT $2 OFFSET $3''',
        author.get('id'), per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page -1 or None
        target['pages'] = await iter_pages(page, last)
        target['aliases'] = [
                {'url': record.get('url'),
                 'parsed': await parse_url(record.get('url')),
                 'created': record.get('created').isoformat(),
                 'clicked': record.get('clicked'),
                 'suffix': record.get('suffix'),
                 'author': author.get('username'),
                 'profile': request.url_for(
                     'people:profile',
                     username=author.get('username'))._url,
                 'canrem': author.get('weight') < cu.get('weight'),
                 'alias': request.url_for(
                     'jump', suffix=record.get('suffix'))._url}
                 for record in query]


async def select_aliases(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT url, created, clicked, suffix FROM aliases
             WHERE author_id = $1
             ORDER BY created DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['aliases'] = [
            {'url': record.get('url'),
             'parsed': await parse_url(record.get('url')),
             'created': record.get('created').isoformat(),
             'clicked': record.get('clicked'),
             'suffix': record.get('suffix'),
             'alias': request.url_for(
                 'jump', suffix=record.get('suffix'))._url}
             for record in query]


async def select_users(
        request, conn, uid, is_admin, target, page, per_page, last):
    if is_admin:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1
                   ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    else:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1 AND weight > 0
                   ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['users'] = [
            {'username': record.get('username'),
             'group': record.get('ugroup'),
             'last_visit': record.get('last_visit').isoformat(),
             'registered': record.get('registered').isoformat(),
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url}
             for record in query]


async def check_last(conn, page, per_page, *args):
    num = await conn.fetchval(*args)
    return math.ceil(num / per_page) or 1


async def rem_session(conn, cu):
    await conn.execute(
        'DELETE FROM sessions WHERE suffix = $1 AND user_id = $2',
        cu.get('ses'), cu.get('id'))
    return 'Брелок скомпрометирован, действие отменено.'


async def check_rel(conn, uid1, uid2):
    friend = bool(await conn.fetchrow(
        '''SELECT author_id, friend_id FROM friends
             WHERE author_id = $1 AND friend_id = $2''', uid1, uid2))
    follower = bool(await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', uid1, uid2))
    blocker = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid2, uid1))
    blocked = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid1, uid2))
    return {'friend': friend, 'follower': follower,
            'blocker': blocker, 'blocked': blocked}


async def filter_target_user(request, conn, username):
    query = await conn.fetchrow(
        '''SELECT id, username, ugroup, weight, registered,
                  last_visit, description, last_published
             FROM users
             WHERE username = $1''', username)
    if query:
        return {'uid': query.get('id'),
                'username': query.get('username'),
                'group': query.get('ugroup'),
                'weight': query.get('weight'),
                'registered': query.get('registered').isoformat(),
                'last_visit': query.get('last_visit').isoformat(),
                'description': query.get('description'),
                'last_published': query.get('last_published').isoformat()
                if query.get('last_published') else None,
                'ava': request.url_for(
                    'ava', username=query.get('username'), size=160)._url}


async def sget_acc(conn, address):
    now = datetime.now(UTC)
    q = 'SELECT id FROM accounts WHERE address = $1 AND user_id IS NULL'
    acc = await conn.fetchval(q, address)
    if acc:
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE id = $2''', now, acc)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested, swexpire)
                 VALUES ($1, $2, $2)''', address, now)
        acc = await conn.fetchval(q, address)
    return acc


async def check_data(config, conn, uid, address):
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE user_id = $1',
        uid)
    length = timedelta(
        seconds=round(3600*config.get('TLENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('RINTERVAL', cast=float)))
    if datetime.now(UTC) - acc.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if acc.get('address') == address:
        return 'Задан ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.now(UTC) - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('RINTERVAL', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.now(UTC) - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


async def check_swap(conn, address):
    swapped = await conn.fetchrow(
        'SELECT id FROM accounts WHERE swap = $1 AND swexpire > $2',
        address, datetime.now(UTC))
    if swapped:
        return True
    return None


async def check_acc(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('RINTERVAL', cast=float)))
    acc = await conn.fetchrow(
        '''SELECT a.address, a.requested, a.id, u.username
             FROM accounts AS a, users AS u
             WHERE a.address = $1
               AND a.user_id = u.id
               AND a.user_id IS NOT NULL''', address)
    if acc is None:
        message = 'Аккаунт не существует.'
    if acc and datetime.now(UTC) - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    return message, acc


async def filter_user(conn, login):
    squery = '''SELECT users.id, users.username,
                       users.password_hash, users.weight
                  FROM users, accounts
                    WHERE users.id = accounts.user_id'''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and query.get('weight'):
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash')}


async def create_session(config, conn, rme, user, brkey):
    now = datetime.now(UTC)
    if rme:
        expire = now + timedelta(
            seconds=config.get('SESSION_LIFETIME', cast=int))
    else:
        expire = now + timedelta(seconds=2*60*60)
    suffix = await get_unique_s(conn, 'sessions', 13)
    await conn.execute(
        '''INSERT INTO sessions (suffix, brkey, logedin, expire, user_id)
             VALUES ($1, $2, $3, $4, $5)''',
        suffix, brkey, now, expire, user.get('id'))
    return suffix, now
