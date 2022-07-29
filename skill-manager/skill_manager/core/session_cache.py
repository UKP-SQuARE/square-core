
import os
import requests_cache
from datetime import timedelta
from skill_manager import redis_client


class SessionCache():

    def init_session(self):
        self._session = requests_cache.CachedSession(
        cache_name="skill_query_cache",
        backend=requests_cache.backends.redis.RedisCache(
            namespace="skill_query_cache", connection=redis_client.client
        ),
        cache_control=True,
        expire_after=timedelta(minutes=os.getenv("CACHE_EXPIRE_MINS", 5)),
        allowable_codes=[200],
        allowable_methods=["GET", "POST"],
        stale_if_error=False,
    )

    @property
    def session(self):
        if not hasattr(self, "_session"):
            self.init_session()
        return self._session
