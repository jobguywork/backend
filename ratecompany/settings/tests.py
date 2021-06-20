from .base import *
from .configs import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

SECRET_KEY = "some-khafan-key"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SMS_BACKEND = "CONSOLE"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "jgdb",
        "USER": "jobguy",
        "PASSWORD": "J0bGUYdB",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
