import os

from starlette.config import Config

base = os.path.dirname(__file__)
templates = os.path.join(base, 'templates')
static = os.path.join(base, 'static')
images = os.path.join(static, 'images')
settings = Config(os.path.join(os.path.dirname(base), '.env'))
