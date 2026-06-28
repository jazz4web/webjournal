import jinja2
import redis.asyncio as redis

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .dirs import settings, static, templates
from .errors import show_error

from .admin.views import admin_aliases, admin_auth_aliases, show_tools
from .aliases.views import show_aliases
from .api.admin import (
    Admin, Alis, AuthAlis, DGroup)
from .api.aliases import Aliases
from .api.auth import CreateAcc, Login, Logout, LogoutE, ResetFP
from .api.main import Captcha, Index
from .api.people import ChangeAva, ChangeM, ChangePasswd, People, Profile
from .api.pictures import Album, Albums, Albumstat, Picstat, Search
from .auth.views import change_mail, reset_fp
from .captcha.views import show_captcha
from .main.views import (
        jump, show_avatar, show_favicon, show_humans,
        show_index, show_picture)
from .people.views import show_people, show_profile
from .pictures.views import show_album, show_albums

try:
    from .tuning import SECRET_KEY, SDESC, MAIL_PASSWORD
    if SECRET_KEY:
        settings.file_values['SECRET_KEY'] = SECRET_KEY
    if SDESC:
        settings.file_values['SDESC'] = SDESC
    if MAIL_PASSWORD:
        settings.file_values['MAIL_PASSWORD'] = MAIL_PASSWORD
except ModuleNotFoundError:
    pass

errs = {403: show_error,
        404: show_error,
        405: show_error}

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int))]


class StApp(Starlette):
    async def __call__(
            self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        self.config = settings
        loader = jinja2.FileSystemLoader(templates)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', cast=bool)
        env = jinja2.Environment(loader=loader, extensions=[assets])
        env.assets_environment = assets_env
        env.globals['config'] = settings
        self.jinja = Jinja2Templates(env=env)
        self.rp = redis.ConnectionPool.from_url(
            settings.get('REDI'),
            health_check_interval=30,
            socket_connect_timeout=15,
            socket_keepalive=True,
            retry_on_timeout=True,
            decode_responses=True)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)


app = StApp(
    debug=settings.get('DEBUG', cast=bool),
    routes=[
        Route('/', show_index, name='index'),
        Route('/favicon.ico', show_favicon, name='favicon'),
        Route('/humans.txt', show_humans, name='humans.txt'),
        Route('/{suffix}', jump, name='jump'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Route('/captcha/{suffix}', show_captcha, name='captcha'),
        Route('/picture/{suffix}', show_picture, name='picture'),
        Mount('/admin', name='admin', routes=[
            Route('/', show_tools, name='tools'),
            Route('/aliases', admin_aliases, name='admaliases'),
            Route('/aliases/{username}', admin_auth_aliases, name='adauthal'),
            ]),
        Mount('/aliases', name='aliases', routes=[
            Route('/', show_aliases, name='aliases')]),
        Mount('/api', name='api', routes=[
            Route('/search', Search, name='asearch'),
            Route('/picstat', Picstat, name='apicstat'),
            Route('/pictures/{suffix}', Album, name='aalbum'),
            Route('/albumstat', Albumstat, name='albumstat'),
            Route('/pictures', Albums, name='aalbums'),
            Route('/admin-auth-aliases', AuthAlis, name='aadmauthaliases'),
            Route('/admin-aliases', Alis, name='aadmaliases'),
            Route('/aliases', Aliases, name='aaliases'),
            Route('/people', People, name='apeople'),
            Route('/chdg', DGroup, name='achdg'),
            Route('/admin-tools', Admin, name='aadmin'),
            Route('/change-m', ChangeM, name='achangem'),
            Route('/change-passwd', ChangePasswd, name='achpwd'),
            Route('/change-ava', ChangeAva, name='achava'),
            Route('/profile', Profile, name='aprofile'),
            Route('/reg', CreateAcc, name='areg'),
            Route('/rfp', ResetFP, name='arfp'),
            Route('/logoutall', LogoutE, name='alogaoutall'),
            Route('/logout', Logout, name='alogout'),
            Route('/login', Login, name='alogin'),
            Route('/index', Index, name='aindex'),
            Route('/captcha', Captcha, name='acaptcha')]),
        Mount('/auth', name='auth', routes=[
            Route('/mail/{token}', change_mail, name='mail'),
            Route('/reg/{token}', reset_fp, name='reg'),
            Route('/rfp/{token}', reset_fp, name='rfp')]),
        Mount('/people', name='people', routes=[
            Route('/', show_people, name='people'),
            Route('/{username}', show_profile, name='profile'),]),
        Mount('/pictures', name='pictures', routes=[
            Route('/', show_albums, name='albums'),
            Route('/{suffix}', show_album, name='album')]),
        Mount('/static', app=StaticFiles(directory=static), name='static')],
    middleware=middleware,
    exception_handlers=errs)
