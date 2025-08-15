from fastapi import APIRouter, status, Response
from redis.asyncio import Redis
import asyncpg
from core.settings import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check(response: Response):
    """
    Checks the health of the service and its dependencies.
    """
    redis_ok = False
    postgres_ok = False

    # Check Redis connection
    try:
        # Note: docker-compose exposes redis on 6380
        redis_client = Redis(host='localhost', port=6380, db=0, decode_responses=True)
        if await redis_client.ping():
            redis_ok = True
        await redis_client.close()
    except Exception:
        pass

    # Check PostgreSQL connection
    try:
        conn = await asyncpg.connect(settings.db_url)
        result = await conn.fetchval('SELECT 1')
        if result == 1:
            postgres_ok = True
        await conn.close()
    except Exception:
        pass

    if redis_ok and postgres_ok:
        return {"status": "ok", "details": {"redis": "ok", "postgres": "ok"}}
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "details": {
                "redis": "ok" if redis_ok else "error",
                "postgres": "ok" if postgres_ok else "error",
            },
        }
