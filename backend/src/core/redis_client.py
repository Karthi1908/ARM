import json
import logging
try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from typing import Optional, Any
from backend.src.core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client: Optional[Any] = None
        self._memory_cache: dict[str, tuple[str, float]] = {}  # key -> (value_json, expire_timestamp)
        self._is_redis_available = False

    async def connect(self):
        if redis is None:
            self._is_redis_available = False
            logger.info("redis package not installed, using in-memory cache.")
            return

        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.client.ping()
            self._is_redis_available = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self._is_redis_available = False
            logger.warning(f"Redis unavailable, falling back to in-memory caching: {e}")

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        if self._is_redis_available and self.client:
            try:
                val = await self.client.get(key)
                return json.loads(val) if val else None
            except Exception as e:
                logger.error(f"Redis get error for {key}: {e}")
        
        # In-memory fallback
        if key in self._memory_cache:
            val, _ = self._memory_cache[key]
            return json.loads(val)
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        serialized = json.dumps(value)
        if self._is_redis_available and self.client:
            try:
                await self.client.set(key, serialized, ex=ttl_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set error for {key}: {e}")

        # In-memory fallback
        import time
        self._memory_cache[key] = (serialized, time.time() + ttl_seconds)
        return True

    async def delete(self, key: str) -> bool:
        if self._is_redis_available and self.client:
            try:
                await self.client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        self._memory_cache.pop(key, None)
        return True

redis_manager = RedisManager()
