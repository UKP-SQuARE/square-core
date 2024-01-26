import logging
import os
from datetime import timedelta

import requests_cache

from profile_manager import redis_client

logger = logging.getLogger(__name__)


class SessionCache:
    def init_session(self):
        self._session = requests_cache.CachedSession(
            cache_name="profile_query_cache",
            backend=requests_cache.backends.redis.RedisCache(
                namespace="profile_query_cache", connection=redis_client.client
            ),
            serializer="json",
            match_headers=False,
            ignored_parameters=["user_id"],
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
