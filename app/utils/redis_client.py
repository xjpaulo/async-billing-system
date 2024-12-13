from redis import Redis


class RedisClient:
    _instance = None

    @staticmethod
    def get_instance():
        if RedisClient._instance is None:
            RedisClient._instance = Redis(
                host="redis",
                port=6379,
                db=0,
                decode_responses=True,
            )
        return RedisClient._instance


redis_client = RedisClient.get_instance()
