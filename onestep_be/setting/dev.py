from accounts.aws import get_secret
from onestep_be.settings import set_sentry_init_setting

SECRETS = eval(get_secret())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": SECRETS.get("DB_NAME"),
        "USER": SECRETS.get("DB_USER"),
        "PASSWORD": SECRETS.get("DB_PASSWORD"),
        "HOST": SECRETS.get("DB_HOST"),
        "PORT": SECRETS.get("DB_PORT"),
    }
}

set_sentry_init_setting("Development")
