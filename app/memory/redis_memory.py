import redis
import json
import os
from redis.asyncio import Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def _key(user_id: str) -> str:
    return f"chat_history:{user_id}"


def get_history(user_id: str) -> list:
    """
    Returns chat history in LangChain-compatible format
    """
    messages = redis_client.lrange(_key(user_id), 0, -1)

    history = []
    for msg in messages:
        history.append(json.loads(msg))

    return history


def save_message(user_id: str, content: str, role: str = "human"):
    """
    Stores one message in Redis
    """
    message = {
        "role": role,
        "content": content
    }

    redis_client.rpush(_key(user_id), json.dumps(message))
