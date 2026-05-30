from datetime import datetime, UTC
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from ..api.tokens import check_token
from ..api.tools import fix_bad_token
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .cu import getcu


async def change_mail(request):
    key = request.path_params.get('token')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    if cu is None:
        await set_flashed(request, 'Авторизуйтесь и повторите запрос.')
        await conn.close()
        return RedirectResponse(
            request.url_for('index')._url  + '?realm=login')
    acc = await check_token(request.app.config, key)
    if acc is None:
        await set_flashed(request, await fix_bad_token(request.app.config))
        await conn.close()
        return RedirectResponse(request.url_for('index'))
    acc = await conn.fetchrow(
        '''SELECT accounts.id, accounts.user_id, accounts.requested,
                  accounts.swap, users.username, users.last_visit
             FROM accounts, users
             WHERE accounts.id = $1 AND accounts.user_id = users.id''',
        acc.get('aid'))
    if acc is None or cu.get('username') != acc.get('username') or \
            acc.get('swap') is None:
        await conn.close()
        await set_flashed(request, 'Данные устарели, действие отменено.')
        return RedirectResponse(request.url_for('index'))
    newacc = await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        acc.get('swap'))
    now = datetime.now(UTC)
    await conn.execute(
        '''UPDATE accounts SET user_id = NULL, swap = NULL,
                               requested = $1, swexpire = $1
             WHERE id = $2''',
        now, acc.get('id'))
    if newacc:
        await conn.execute(
            '''UPDATE accounts SET requested = $1, swexpire = $1, user_id = $2
                 WHERE id = $3''',
            now, cu.get('id'), newacc.get('id'))
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested, swexpire, user_id)
                 VALUES ($1, $2, $2, $3)''',
            acc.get('swap'), now, cu.get('id'))
    await conn.close()
    await set_flashed(
        request, f'Внимание, {cu.get("username")}, у вас новый адрес.')
    return RedirectResponse(
        request.url_for('people:profile', username=cu.get('username')))


async def reset_fp(request):
    key = request.path_params.get('token')
    if len(key) < 100:
        raise HTTPException(404)
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    view = request['path'].split('/')[2]
    template = f'auth/{view}.html'
    return request.app.jinja.TemplateResponse(
        request, template,
        {'key': key,
         'cu': cu,
         'interval': request.app.config.get(
             'RINTERVAL', cast=float),
         'listed': False})
