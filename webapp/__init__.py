import jinja2

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .dirs import settings, static, templates

from .main.views import show_avatar, show_favicon, show_humans, show_index


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
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)


app = StApp(
    debug=settings.get('DEBUG', cast=bool),
    routes=[
        Route('/', show_index, name='index'),
        Route('/favicon.ico', show_favicon, name='favicon'),
        Route('/humans.txt', show_humans, name='humans.txt'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Mount('/static', app=StaticFiles(directory=static), name='static')
        ])

