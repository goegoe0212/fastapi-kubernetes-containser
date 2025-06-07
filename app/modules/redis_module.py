import redis

class RedisConnector:
    def __init__(self, host='redis', port=6379, max_connections=10):
        self.host = host
        self.port = port
        self._pool = None
        self.max_connections = max_connections

    def _initialize_pool(self):
        if self._pool is None:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                max_connections=self.max_connections,
                decode_responses=True
            )

    def get_connection(self):
        if self._pool is None:
            self._initialize_pool()
        return redis.Redis(connection_pool=self._pool)
