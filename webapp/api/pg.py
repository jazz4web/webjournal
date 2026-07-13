import asyncio
import functools
import math

from datetime import datetime, timedelta, UTC

from validate_email import validate_email

from ..common.aparsers import (
    iter_pages, parse_pic_filename, parse_title, parse_units, parse_url)
from ..common.random import get_unique_s
from ..drafts.attri import status
from ..pictures.attri import status as sta
from .parse import parse_art_query, parse_arts_query
from .slugs import check_max, make, parse_match


async def check_draft(request, conn, slug, cuid, target):
    query = await conn.fetchrow(
        '''SELECT articles.id, articles.title, articles.slug,
                  articles.suffix, articles.html, articles.summary,
                  articles.meta, articles.published, articles.edited,
                  articles.state, articles.commented, articles.viewed,
                  articles.author_id, users.username
             FROM articles, users
             WHERE articles.slug = $1
               AND articles.author_id = $2
               AND users.id = articles.author_id''',
        slug, cuid)
    if query:
        await parse_art_query(request, conn, query, target)


async def check_slug(conn, title):
    loop = asyncio.get_running_loop()
    slug = await loop.run_in_executor(
        None, functools.partial(make, title))
    match = await conn.fetch(
        'SELECT slug FROM articles WHERE slug LIKE $1', f'{slug}%')
    match = await loop.run_in_executor(
        None, functools.partial(parse_match, match))
    if not match or slug not in match:
        return slug
    maxi = await loop.run_in_executor(
        None, functools.partial(check_max, match, slug))
    return f'{slug}-{maxi+1}'


async def create_d(conn, title, uid):
    suffix = await get_unique_s(conn, 'articles', 8)
    slug = await check_slug(conn, title)
    now = datetime.now(UTC)
    empty = await conn.fetchval(
        'SELECT id FROM articles WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE articles
                 SET title = $1, slug = $2, suffix = $3,
                     edited = $4, state = $5, author_id = $6
                 WHERE id = $7''',
            title, slug, suffix, now, status.draft, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO articles
               (title, slug, suffix, edited, state, author_id)
               VALUES ($1, $2, $3, $4, $5, $6)''',
            title, slug, suffix, now, status.draft, uid)
    return slug


async def select_drafts(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.state IN ($2, $3)
             ORDER BY a.edited DESC LIMIT $4 OFFSET $5''',
        uid, status.draft, status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def sadmin_auth_pictures(
        request, conn, author, cu, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT p.uploaded, p.filename, p.width, p.height,
                  p.volume, p.suffix, p.format, a.title,
                  a.suffix AS album, u.username, u.weight
             FROM pictures AS p, albums AS a, users AS u
             WHERE p.album_id = a.id
               AND a.author_id = u.id
               AND a.state IN ($1, $2)
               AND u.id = $3
               ORDER BY p.uploaded DESC LIMIT $4 OFFSET $5''',
        sta.pub, sta.priv, author.get('id'), per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['pictures'] = [
            {'author': picture.get('username'),
             'profile': request.url_for(
                 'people:profile',
                 username=picture.get('username'))._url,
             'canrem': picture.get('weight') < cu.get('weight'),
             'album': request.url_for(
                 'admin:admalbum',
                 album=picture.get('album'))._url,
             'albumtitle': await parse_title(
                 picture.get('title'), 100),
             'filename': await parse_pic_filename(
                 picture.get('filename'), 100),
             'format': picture.get('format'),
             'volume': await parse_units(picture.get('volume')),
             'width': picture.get('width'),
             'height': picture.get('height'),
             'uploaded': picture.get('uploaded').isoformat(),
             'suffix': picture.get('suffix'),
             'url': request.url_for(
                 'picture',
                 suffix=picture.get('suffix'))._url}
            for picture in query]


async def sadmin_album(
        request, conn, album, cu, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT p.uploaded, p.filename, p.width, p.height,
                  p.volume, p.suffix, p.format, a.title,
                  a.suffix AS album, u.username, u.weight
             FROM pictures AS p, albums AS a, users AS u
             WHERE p.album_id = a.id
               AND a.author_id = u.id
               AND a.state IN ($1, $2)
               AND a.id = $3
               ORDER BY p.uploaded DESC LIMIT $4 OFFSET $5''',
        sta.pub, sta.priv, album.get('id'), per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['pictures'] = [
            {'author': picture.get('username'),
             'profile': request.url_for(
                 'people:profile',
                 username=picture.get('username'))._url,
             'canrem': picture.get('weight') < cu.get('weight'),
             'album': request.url_for(
                 'admin:admalbum',
                 album=picture.get('album'))._url,
             'albumtitle': await parse_title(
                 picture.get('title'), 100),
             'filename': await parse_pic_filename(
                 picture.get('filename'), 100),
             'format': picture.get('format'),
             'volume': await parse_units(picture.get('volume')),
             'width': picture.get('width'),
             'height': picture.get('height'),
             'uploaded': picture.get('uploaded').isoformat(),
             'suffix': picture.get('suffix'),
             'url': request.url_for(
                 'picture',
                 suffix=picture.get('suffix'))._url}
            for picture in query]


async def get_pic_stat(request, conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT pictures.uploaded, pictures.filename, pictures.width,
                  pictures.height, pictures.format, pictures.volume,
                  pictures.suffix, albums.author_id FROM pictures, albums
             WHERE pictures.album_id = albums.id
               AND albums.author_id = $1 AND pictures.suffix = $2''',
        uid, suffix)
    if query:
        return {'uploaded': query.get('uploaded').isoformat(),
                'filename': query.get('filename'),
                'width': query.get('width'),
                'height': query.get('height'),
                'format': query.get('format'),
                'volume': await parse_units(query.get('volume')),
                'suffix': query.get('suffix'),
                'url': request.url_for(
                    'picture', suffix=query.get('suffix'))._url,
                'path': request.app.url_path_for(
                    'picture', suffix=query.get('suffix')),
                'parsed': await parse_pic_filename(
                    query.get('filename'), 60)}


async def select_pictures(conn, aid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT filename, suffix FROM pictures
             WHERE album_id = $1
             ORDER BY uploaded DESC LIMIT $2 OFFSET $3''',
        aid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'pictures': [{'filename': record.get('filename'),
                              'longer': len(record.get('filename')) > 60,
                              'parsed': await parse_pic_filename(
                                  record.get('filename'), 60),
                              'suffix': record.get('suffix')}
                             for record in query]}


async def get_album(conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT id, title, created, suffix, state, volume FROM albums
             WHERE suffix = $1 AND author_id = $2''',
        suffix, uid)
    if query:
        num = await conn.fetchval(
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            query.get('id'))
        return {'id': query.get('id'),
                'title': query.get('title'),
                'created': query.get('created').isoformat(),
                'suffix': query.get('suffix'),
                'state': query.get('state'),
                'volume_': query.get('volume'),
                'volume': await parse_units(query.get('volume')),
                'files': num,
                'parsed': await parse_title(query.get('title'), 65)}
    return None


async def create_new_album(conn, uid, title, state):
    now = datetime.now(UTC)
    suffix = await get_unique_s(conn, 'albums', 8)
    empty = await conn.fetchval(
        'SELECT id FROM albums WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE albums SET title = $1,
                                 created = $2,
                                 changed = $2,
                                 suffix = $3,
                                 state = $4,
                                 volume = 0,
                                 author_id = $5 WHERE id = $6''',
            title, now, suffix, state, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO
                 albums (title, created, changed, suffix, state, author_id)
                 VALUES ($1, $2, $2, $3, $4, $5)''',
            title, now, suffix, state, uid)
    return suffix


async def select_albums(conn, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 65)
                            if len(record.get('title')) > 65 else None,
                            'suffix': record.get('suffix')}
                           for record in query]}


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1''', uid) or 0)}


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
