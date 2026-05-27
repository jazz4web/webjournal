from datetime import datetime, timedelta, UTC

from validate_email import validate_email

from ..common.random import get_unique_s


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
