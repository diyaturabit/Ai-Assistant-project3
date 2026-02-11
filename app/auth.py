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
    print(f"Token api calling Response:",response)
    response.raise_for_status()

    token = response.json()["access_token"]
    print(f"Token generated variabble storing:",token)
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


# import httpx
# from app.memory.redis_memory import redis_client   # import your existing redis
# from config import PROJECT1_URL

# TOKEN_KEY = "project3_admin_jwt"


# async def login_admin(email: str, password: str):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={
#                 "email": email, 
#                 "password": password
#             },
#             timeout=10
#         )
#     print(f"Token api calling Response:",response)
#     response.raise_for_status()

#     token = response.json()["access_token"]
#     print(f"Token generated variabble storing:",token)
#     # Cache token for 1 hour
#     redis_client.setex(TOKEN_KEY, 3600, token)

#     return token


# async def get_admin_token():
#     """
#     Fetch token from Redis or login again
#     """
#     token = redis_client.get(TOKEN_KEY)

#     if token:
#         return token

#     return await login_admin(email,password)



# import httpx
# from app.memory.redis_memory import redis_client   # your async Redis client
# from config import PROJECT1_URL

# TOKEN_EXPIRY_SECONDS = 3600  # 1 hour expiry


# async def login_user(email: str, password: str) -> str:
#     """
#     Call the login API for a given user and store their token in Redis.
#     """
#     async with httpx.AsyncClient(timeout=10) as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={"email": email, "password": password},
#         )
#     response.raise_for_status()

#     data = response.json()
#     token = data.get("access_token")
#     if not token:
#         raise ValueError("No access_token returned by API")

#     # Store token in Redis with email as key
#     await redis_client.set(f"user_token:{email}", token, ex=TOKEN_EXPIRY_SECONDS)
#     print(f"Token stored in Redis for {email}: {token}")
#     return token


# async def get_admin_token(email: str) -> str:
#     """
#     Fetch token from Redis. If not found, raise error.
#     """
#     token = await redis_client.get(f"user_token:{email}")
#     if not token:
#         raise ValueError(f"Token for {email} not found or expired. Login required.")
#     return token


# # auth.py
# import httpx
# from app.memory.redis_memory import redis_client
# from config import PROJECT1_URL

# TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

# async def login_user_via_api(email: str, password: str) -> str:
#     """
#     Call Project 1 login API, get access_token, store in Redis.
#     """
#     async with httpx.AsyncClient(timeout=10) as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={"email": email, "password": password}
#         )

#     if response.status_code != 200:
#         raise ValueError(f"Login failed: {response.json().get('error', 'Unknown error')}")

#     token = response.json().get("access_token")
#     if not token:
#         raise ValueError("No access_token returned by API")

#     # store token in Redis (async)
#     await redis_client.set(f"user_token:{email}", token, ex=3600)
#     return token


# async def get_admin_token(email: str) -> str:
#     """
#     Fetch token from Redis. If missing, login again.
#     """
#     # fetch token
#     token = await redis_client.get(f"user_token:{email}")
#     if not token:
#         # login automatically if token missing
#         # you will need the password somehow; or prompt user to login
#         raise ValueError("User token not found or expired")
#     return token


# import httpx
# import asyncio
# from app.memory.redis_memory import redis_client  # your existing Redis client
# # from config import PROJECT1_URL
# PROJECT1_URL="http://192.168.1.70:5000"

# TOKEN_KEY = "project3_admin_jwt"
# CREDENTIALS_KEY = "project3_admin_credentials"  # Redis key to store admin email/password


# async def login_admin(email=None, password=None):
#     """
#     Login admin dynamically using credentials.
#     If email/password not provided, fetch from Redis.
#     """
#     if not email or not password:
#         creds = redis_client.get(CREDENTIALS_KEY)
#         if not creds:
#             raise ValueError("Admin credentials not found in Redis")
#         creds = creds.decode() if isinstance(creds, bytes) else creds
#         email, password = creds.split(":")

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={"email": email, 
#                   "password": password}
#         )
#         print("Auth response:", response)
#         response.raise_for_status()

#     token = response.json()["access_token"]
#     redis_client.setex(TOKEN_KEY, 3600, token)
#     print(f"Admin token cached: {token}")
#     return token


# async def get_admin_token():
#     """
#     Fetch token from Redis or login again dynamically.
#     """
#     token = redis_client.get(TOKEN_KEY)
#     print("Redis token:", token)
#     if token:
#         return token.decode() if isinstance(token, bytes) else token

#     return await login_admin()

# # get_admin_token()

# auth.py
# import asyncio
# import httpx
# from app.memory.redis_memory import redis_client  # your Redis client

# PROJECT1_URL = "http://192.168.1.70:5000"  # change to your API base URL
# TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

# async def login_user_via_api(email: str, password: str) -> str:
#     """
#     Call the login API, get access_token, and store it in Redis.
#     """
#     async with httpx.AsyncClient(timeout=10) as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={"email": email, "password": password}
#         )
#         print(f"Token api calling Response:",response)

#     if response.status_code != 200:
#         raise ValueError(f"Login failed: {response.json().get('error', 'Unknown error')}")

#     data = response.json()
#     print(f"Data",data)
#     token = data.get("access_token")
#     if not token:
#         raise ValueError("No access_token returned by API")

#     # Store token in Redis with expiry
#     await redis_client.set(f"user_token:{email}", token, ex=TOKEN_EXPIRY_SECONDS)
#     return token

# async def get_admin_token(email: str) -> str:
#     """
#     Retrieve the user's token from Redis. Raise error if not found or expired.
#     """
#     token = await redis_client.get(f"user_token:{email}")
#     print(f"TOken:",token)
#     if not token:
#         raise ValueError("User token not found or expired")
#     return token
# import asyncio
# import httpx
# import aioredis

# PROJECT1_URL = "http://192.168.1.70:5000"
# TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

# # Initialize async Redis client
# redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# async def login_user_via_api(email: str, password: str) -> str:
#     """
#     Call Project 1 login API, get access_token, and store in Redis.
#     """
#     async with httpx.AsyncClient(timeout=10) as client:
#         response = await client.post(
#             f"{PROJECT1_URL}/auth/login",
#             json={"email": email, "password": password},
#         )

#     if response.status_code != 200:
#         raise ValueError(f"Login failed: {response.json().get('error', 'Unknown error')}")

#     data = response.json()
#     token = data.get("access_token")
#     if not token:
#         raise ValueError("No access_token returned by API")

#     # Store token in Redis with expiry
#     await redis_client.set(f"user_token:{email}", token, ex=TOKEN_EXPIRY_SECONDS)
#     return token


# async def get_admin_token(email: str) -> str:
#     """
#     Retrieve token for a user from Redis. Raises error if not found or expired.
#     """
#     token = await redis_client.get(f"user_token:{email}")
#     if not token:
#         raise ValueError("User token not found or expired")
#     return token
