
from onestep_be.settings import *


SKIP_AUTHENTICATION = True

if SKIP_AUTHENTICATION:
    MIDDLEWARE.insert(0, "accounts.middleware.SkipAuthMiddleware")

set_sentry_init_setting("Testing")