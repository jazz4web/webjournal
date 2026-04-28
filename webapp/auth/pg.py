from datetime import datetime, UTC

from passlib.hash import pbkdf2_sha256

from ..common.pg import get_conn

from .attri import groups


async def check_username(config, username):
    conn = await get_conn(config)
    res = await conn.fetchrow(
        'SELECT username FROM users WHERE username = $1', username)
    await conn.close()
    return bool(res)


async def check_address(config, address):
    res = False
    conn = await get_conn(config)
    account = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    now = datetime.now(UTC)
    swap = await conn.fetchrow(
        '''SELECT swap FROM accounts
             WHERE swap = $1 AND swexpire > $2''', address, now)
    await conn.close()
    if (account and account.get('user_id')) or swap:
        res = True
    return res


async def update_account(conn, address, uid, now):
    account = await conn.fetchrow(
        'SELECT * FROM accounts WHERE address = $1', address)
    if account:
        await conn.execute(
            '''UPDATE accounts
                 SET user_id = $1, requested = $2 WHERE address = $3''',
            uid, now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, swexpire, requested, user_id)
                 VALUES ($1, $2, $2, $3)''', address, now, uid)


async def create_user_record(conn, username, passwd, group, now):
    await conn.execute(
        '''INSERT INTO users
           (username, ugroup, weight, registered, last_visit, password_hash)
           VALUES ($1, $2, $3, $4, $5, $6)''',
        username, group, groups.weigh(group),
        now, now, pbkdf2_sha256.hash(passwd))
    return await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)


async def create_user(config, username, address, passwd, group):
    now = datetime.now(UTC)
    conn = await get_conn(config)
    user_id = await create_user_record(conn, username, passwd, group, now)
    await update_account(conn, address, user_id, now)
    await conn.close()
