import asyncio
import functools

from datetime import datetime, UTC

from aiosmtplib import send
from email.message import EmailMessage

from ..captcha.common import check_suffix, check_val
from ..captcha.picturize.picture import generate_image
from ..common.pg import get_conn
from .tokens import create_request_token


async def send_rfp_mail(request, acc):
    token = await create_request_token(request, acc.get('id'))
    url = request.url_for('auth:rfp', token=token)
    content = request.app.jinja.get_template('emails/rfp.html').render(
            username=acc.get('username'),
            index=request.url_for('index'),
            target=url, length=request.app.config.get('TLENGTH', cast=float),
            interval=request.app.config.get('RINTERVAL', cast=float))
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = acc.get('address')
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + 'Сброс забытого пароля'
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[acc.get('address')],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))
    return None


async def rem_old_session(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'DELETE FROM sessions WHERE user_id = $1 AND expire < $2',
        uid, datetime.now(UTC))
    sessions = [record.get('suffix') for record in await conn.fetch(
        '''SELECT suffix FROM sessions
             WHERE user_id = $1
             ORDER BY logedin ASC''', uid)]
    if len(sessions) > 3:
        await conn.execute(
            'DELETE FROM sessions WHERE suffix = $1', sessions[0])
    await conn.close()


async def change_pattern(conf, suffix):
    conn = await get_conn(conf)
    pre = await conn.fetchval(
        'SELECT suffix FROM captchas WHERE suffix = $1', suffix)
    if pre:
        val = await check_val(conn)
        new = await check_suffix(conn)
        loop = asyncio.get_running_loop()
        pic = await loop.run_in_executor(
            None, functools.partial(generate_image, val))
        await conn.execute(
            '''UPDATE captchas
                 SET val = $1, picture = $2 WHERE suffix = $3''',
            val, pic.read(), suffix)
        await conn.execute(
            'UPDATE captchas SET suffix = $1 WHERE val = $2', new, val)
        await loop.run_in_executor(
            None, functools.partial(pic.close))
    await conn.close()
    return None


async def ping_user(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'UPDATE users SET last_visit = $1 WHERE id = $2',
        datetime.now(UTC), uid)
    await conn.close()
