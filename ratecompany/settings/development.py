import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env.development")
load_dotenv(dotenv_path)

from .base import *
from .configs import *


DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ.get("SECRET_KEY", None)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SMS_BACKEND = 'CONSOLE'

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "localhost",
        "PORT": 5432,
    }
}
