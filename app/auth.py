import httpx
from app.memory.redis_memory import redis_client   # import your existing redis
from config import PROJECT1_URL

TOKEN_KEY = "project3_admin_jwt"


async def login_admin():
    """
    Manual admin login (one-time)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PROJECT1_URL}/auth/login",
            json={
                "email": "admin@gmail.com",
                "password": "diya123"
            },
            timeout=10
        )

    response.raise_for_status()

    token = response.json()["access_token"]

    # Cache token for 1 hour
    redis_client.setex(TOKEN_KEY, 3600, token)

    return token


async def get_admin_token():
    """
    Fetch token from Redis or login again
    """
    token = redis_client.get(TOKEN_KEY)

    if token:
        return token

    return await login_admin()
