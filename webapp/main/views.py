import os

from starlette.responses import FileResponse, PlainTextResponse

from ..dirs import images


async def show_humans(request):
    text = request.app.jinja.get_template(
        'main/humans.txt').render(request=request)
    return PlainTextResponse(text)


async def show_favicon(request):
    if request.method == 'GET':
        response = FileResponse(
            os.path.join(images, 'favicon.ico'))
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'FILE_MAX_AGE', cast=int, default=0)))
        return response


async def show_index(request):
    cu = None
    return request.app.jinja.TemplateResponse(
        request, 'main/index.html', {'cu': cu})
