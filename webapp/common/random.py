from random import choice, shuffle
from string import ascii_letters, ascii_lowercase, digits

## look at custom.js const samples
samples = (
    'chery',
    'jerry',
    'ammy',
    'woody',
    'znoby',
    'bodhi',
    'samuel',
    'tracy',
    'gracy',
    'poty',
    'alister',
    'reno',
    'wannoty',
    'vero',
    'albano')


async def randomize(n):
    return ''.join(choice(ascii_letters + digits) for _ in range(n))


async def randomize_lower(n):
    cache = list(ascii_lowercase + digits)
    if n > len(cache):
        return None
    shuffle(cache)
    return ''.join(cache[:n])

