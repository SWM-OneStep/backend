from onestep_be.settings import MIDDLEWARE

SKIP_AUTHENTICATION = True

if SKIP_AUTHENTICATION:
    MIDDLEWARE.insert(0, "accounts.middleware.SkipAuthMiddleware")
