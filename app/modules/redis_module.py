from fastapi import HTTPException
import redis
from settings.config import settings


class RedisConnector:
    def __init__(
        self,
        host=settings.redis_host,
        port=settings.redis_port,
        max_connections=settings.redis_max_connections,
    ):
        self.host = host
        self.port = port
        self._pool = None
        self.max_connections = max_connections

    def _initialize_pool(self):
        if self._pool is None:
            try:
                self._pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    max_connections=self.max_connections,
                    decode_responses=True,
                )
            except redis.ConnectionError as e:
                raise HTTPException(
                    status_code=500, detail=f"Redis connection error: {str(e)}"
                )

    def get_connection(self):
        if self._pool is None:
            self._initialize_pool()
        return redis.Redis(connection_pool=self._pool)
