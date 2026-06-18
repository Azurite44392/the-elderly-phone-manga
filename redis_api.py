import redis
from config import REDIS_PORT, REDIS_HOST, REDIS_USERNAME, REDIS_PASSWORD

connection_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True,
                                       retry_on_timeout=5, max_connections=1024, password=REDIS_PASSWORD, username=REDIS_USERNAME)


def get_session():
    return redis.Redis(connection_pool=connection_pool)


if __name__ == "__main__":
    pass
