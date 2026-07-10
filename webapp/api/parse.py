from ..common.aparsers import iter_pages, parse_title
async def parse_arts_query(request, conn, query, target, page, last):
    target['page'] = page
    target['next'] = page + 1 if page + 1 <= last else None
    target['prev'] = page - 1 or None
    target['pages'] = await iter_pages(page, last)
    target['articles'] = [
            {'id': record.get('id'),
             'title': record.get('title'),
             'title80': await parse_title(record.get('title'), 80),
             'slug': record.get('slug'),
             'suffix': record.get('summary'),
             'published': record.get('published').isoformat()
             if record.get('published') else None,
             'edited': record.get('edited').isoformat(),
             'state': record.get('state'),
             'commented': record.get('commented'),
             'viewed': record.get('viewed'),
             'author': record.get('username'),
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url,
             'likes': 0,
             'dislikes': 0,
             'commentaries': 0,
             'labels': None} for record in query]
