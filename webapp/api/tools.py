from ..auth.attri import groups


async def check_profile_permissions(cu, user, data, rel):
    data['rel'] = rel
    data['owner'] = cu.get('id') == user.get('uid')
    data['acts'] = user.get('weight') > 0 and cu.get('weight') > 15 and \
                   ((cu.get('weight') >= 30 and user.get('weight') >= 30 and
                    not rel['blocker'] and not rel['blocked']) or \
                   (cu.get('weight') < 200 and user.get('weight') < 200) or \
                   (cu.get('weight') >= 100 and
                    not rel['blocked'] and not rel['blocker']))
    data['mfriend'] = cu.get('weight') >= 100 and not rel['blocked'] and \
            not rel['blocker']
    data['pm'] = cu.get('weight') >= 30 and user.get('weight') >= 30 and \
            not rel['blocked'] and not rel['blocker']
    data['block'] = cu.get('weight') < 200 and cu.get('weight') >= 30 and \
            user.get('weight') < 200
    data['address'] = cu.get('id') == user.get('uid') or \
            (cu.get('weight') >= 200 and user.get('weight') < 250) or \
            cu.get('weight') >= 250
    data['description'] = (cu.get('weight') >= 100 and
                           cu['id'] == user['uid']) or user['description']
    data['chgroup'] = cu.get('id') != user.get('uid') and \
            cu.get('weight') == 255 or \
            (cu.get('weight') in (200, 250) and user.get('weight') < 200)
    if data.get('chgroup'):
        if cu.get('weight') in (200, 250):
            data['groups'] = groups.keeper_groups()
        if cu.get('weight') == 255:
            data['groups'] = groups.groups()


async def check_permissions(cu, weight):
    if cu is None:
        return 'Доступ ограничен, требуется авторизация.'
    if weight and cu.get('weight') < weight:
        return 'Доступ ограничен, у вас недостаточно прав.'


async def check_g_secure(request, cu, weight):
    message = None
    ses = request.headers.get('x-br-ses')
    if cu and request.app.config.get('SECURE', cast=bool):
        if not ses or request.session.get('_uid') != ses:
            message = "Упс..!"
            return message
    if cu and cu.get('ses') != ses:
        message = "Авторизация недействительна."
        return message
    return await check_permissions(cu, weight)


async def fix_bad_token(config):
    length = config.get('TLENGTH')
    return f'Данные устарели, срок действия брелка {length} часов.'


async def check_secure(request):
    message = None
    ses, brkey = (
        request.headers.get('x-br-ses'), request.headers.get('x-br-tee'))
    if request.app.config.get('SECURE', cast=bool):
        if not ses or request.session.get('_uid') != ses:
            message = "Упс..!"
    return ses, brkey, message
