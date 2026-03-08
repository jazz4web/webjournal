async def get_flashed(request):
    if current := request.session.get('flashed'):
        del request.session['flashed']
        return current


async def set_flashed(request, message):
    if request.session.get('flashed', None) is None:
        request.session['flashed'] = [message]
    else:
        request.session['flashed'].append(message)
