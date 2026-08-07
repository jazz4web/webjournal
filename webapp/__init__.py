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

from .admin.views import (
    admin_album, admin_aliases, admin_au_pic, admin_auth_aliases,
    admin_pictures, show_tools)
from .announces.views import show_announce, show_announces
from .aliases.views import show_aliases
from .api.admin import (
    Admin, AdminAlbum, Alis, AuthAlis, AuthPics, DGroup, Pics, Robots)
from .api.announces import Announce, Announces, Broadcast
from .api.aliases import Aliases
from .api.arts import (
    Art, Arts, Alabels, CArt, CArts, Dislike, LCArts, Lenta, Like, LLenta)
from .api.auth import CreateAcc, Login, Logout, LogoutE, ResetFP
from .api.blogs import Authors, Blog, LBlog
from .api.drafts import Draft, Drafts, Labels, Paragraph
from .api.main import Captcha, Index
from .api.people import ChangeAva, ChangeM, ChangePasswd, People, Profile
from .api.pictures import Album, Albums, Albumstat, Picstat, Search
from .arts.views import (
    show_art, show_arts, show_cart, show_carts,
    show_followed, show_larts, show_lcarts, show_lfollowed)
from .auth.views import change_mail, reset_fp
from .blogs.views import show_blog, show_blogs, show_lblog
from .captcha.views import show_captcha
from .comments.views import show_comments
from .drafts.views import show_draft, show_drafts, show_dlabeled
from .main.views import (
        jump, show_avatar, show_favicon, show_humans,
        show_index, show_picture, show_public, show_robots,
        show_sitemap)
from .people.views import show_people, show_profile
from .pictures.views import show_album, show_albums
from .pm.views import show_conversation, show_conversations

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
        Route('/robots.txt', show_robots, name='robots.txt'),
        Route('/sitemap.xml', show_sitemap, name='sitemap'),
        Route('/{suffix}', jump, name='jump'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Route('/captcha/{suffix}', show_captcha, name='captcha'),
        Route('/picture/{suffix}', show_picture, name='picture'),
        Route('/public/{slug}', show_public, name='public'),
        Mount('/admin', name='admin', routes=[
            Route('/', show_tools, name='tools'),
            Route('/aliases', admin_aliases, name='admaliases'),
            Route('/aliases/{username}', admin_auth_aliases, name='adauthal'),
            Route('/pictures', admin_pictures, name='admpictures'),
            Route('/pictures/a/{album}', admin_album, name='admalbum'),
            Route('/pictures/au/{username}', admin_au_pic, name='aapic')]),
        Mount('/announces', name='announces', routes=[
            Route('/', show_announces, name='announces'),
            Route('/{suffix}', show_announce, name='announce')]),
        Mount('/aliases', name='aliases', routes=[
            Route('/', show_aliases, name='aliases')]),
        Mount('/api', name='api', routes=[
            Route('/chrobots', Robots, name='arobots'),
            Route('/lcarts', LCArts, name='alcarts'),
            Route('/carts', CArts, name='acarts'),
            Route('/llenta', LLenta, name='allenta'),
            Route('/alabels', Alabels, name='alabels'),
            Route('/arts', Arts, name='aarts'),
            Route('/lblog', LBlog, name='alblog'),
            Route('/blog', Blog, name='ablog'),
            Route('/blogs', Authors, name='ablogs'),
            Route('/broadcast', Broadcast, name='abroadcast'),
            Route('/announce', Announce, name='aannounce'),
            Route('/announces', Announces, name='aannounces'),
            Route('/cart', CArt, name='acart'),
            Route('/follow', Lenta, name='afollow'),
            Route('/dislike', Dislike, name='adislike'),
            Route('/like', Like, name='alike'),
            Route('/art', Art, name='aart'),
            Route('/send-par', Paragraph, name='aparagraph'),
            Route('/labels', Labels, name='alabels'),
            Route('/draft', Draft, name='adraft'),
            Route('/drafts', Drafts, name='adrafts'),
            Route('/admin-auth-pictures', AuthPics, name='aadmauthpictures'),
            Route('/admin-album', AdminAlbum, name='aadmalbum'),
            Route('/admin-pictures', Pics, name='aadmpictures'),
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
        Mount('/arts', name='arts', routes=[
            Route('/', show_arts, name='arts'),
            Route('/a/{slug}', show_art, name='art'),
            Route('/c/', show_carts, name='carts'),
            Route('/c/{slug}', show_cart, name='cart'),
            Route('/c/t/{label}', show_lcarts, name='lcarts'),
            Route('/l/', show_followed, name='lenta'),
            Route('/l/t/{label}', show_lfollowed, name='llenta'),
            Route('/t/{label}', show_larts, name='labeled-arts')]),
        Mount('/auth', name='auth', routes=[
            Route('/mail/{token}', change_mail, name='mail'),
            Route('/reg/{token}', reset_fp, name='reg'),
            Route('/rfp/{token}', reset_fp, name='rfp')]),
        Mount('/blogs', name='blogs', routes=[
            Route('/', show_blogs, name='blogs'),
            Route('/{username}', show_blog, name='blog'),
            Route('/{username}/t/{label}', show_lblog, name='lblog')]),
        Mount('/comments', name='comments', routes=[
            Route('/', show_comments, name='comments')]),
        Mount('/drafts', name='drafts', routes=[
            Route('/', show_drafts, name='drafts'),
            Route('/{slug}', show_draft, name='draft'),
            Route('/t/{label}', show_dlabeled, name='draft-labeled')]),
        Mount('/people', name='people', routes=[
            Route('/', show_people, name='people'),
            Route('/{username}', show_profile, name='profile'),]),
        Mount('/pictures', name='pictures', routes=[
            Route('/', show_albums, name='albums'),
            Route('/{suffix}', show_album, name='album')]),
        Mount('/pm', name='pm', routes=[
            Route('/', show_conversations, name='conversations'),
            Route('/{username}', show_conversation, name='conversation')]),
        Mount('/static', app=StaticFiles(directory=static), name='static')],
    middleware=middleware,
    exception_handlers=errs)
