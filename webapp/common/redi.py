import redis.asyncio as redis


async def get_rc(request):
    return redis.Redis.from_pool(request.app.rp)
