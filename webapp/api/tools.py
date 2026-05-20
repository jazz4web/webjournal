async def check_secure(request):
    message = None
    ses, brkey = (
        request.headers.get('x-br-ses'), request.headers.get('x-br-tee'))
    if request.app.config.get('SECURE', cast=bool):
        if not ses or request.session.get('_uid') != ses:
            message = "Упс..!"
    return ses, brkey, message
