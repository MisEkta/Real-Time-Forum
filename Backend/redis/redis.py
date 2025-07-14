import redis
import json
from typing import Any, Optional

class RedisCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._instance.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, expire: int = 300):  # Default 5 minutes cache
        self.redis_client.setex(
            name=key,
            time=expire,
            value=json.dumps(value)
        )

    def delete(self, key: str):
        self.redis_client.delete(key)

    def clear(self):
        self.redis_client.flushdb()