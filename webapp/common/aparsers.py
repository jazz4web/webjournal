from urllib.parse import urlparse


async def parse_url(url):
    l = ''.join(urlparse(url)[1:])
    if len(l) > 50:
        l = l[:49] + '~'
    return l


async def iter_pages(page, last_page):
    if last_page <= 9:
        return list(range(1, last_page + 1))
    if page <= 6:
        return [i for i in range(1, 7)] + [0] + \
               [i for i in range(last_page - 1, last_page + 1)]
    if page >= last_page - 5:
        return [i for i in range(1, 3)] + [0] + \
               [i for i in range(last_page - 5, last_page +1)]
    return [i for i in range(1, 3)] + [0] + \
           [i for i in range(page - 1, page + 2)] + \
           [0] + [i for i in range(last_page - 1, last_page + 1)]


async def parse_page(request):
    page = request.query_params.get('page', None)
    try:
        page = int(page)
    except (ValueError, TypeError):
        return 1
    return page or 1
