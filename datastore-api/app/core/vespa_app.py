from vespa.application import Vespa

from .config import settings


vespa_app = Vespa(url=settings.VESPA_APP_URL)
