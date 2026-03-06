import asyncpg


async def get_conn(config):
    user = config.get('DBUSER', default=None)
    db = config.get('DB', default=None)
    if user and db:
        conn = await asyncpg.connect(user=user, database=db)
    else:
        conn = await asyncpg.connect(config.get('DSN'))
    return conn
