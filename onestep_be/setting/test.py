from onestep_be.settings import MIDDLEWARE, set_sentry_init_setting

SKIP_AUTHENTICATION = True

if SKIP_AUTHENTICATION:
    MIDDLEWARE.insert(0, "accounts.middleware.SkipAuthMiddleware")
    MIDDLEWARE.remove("todos.middleware.FCMAlarmMiddleware")

set_sentry_init_setting("Testing")
