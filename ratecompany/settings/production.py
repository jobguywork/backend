from ratecompany.settings.base import *
from ratecompany.settings.configs import *

import sentry_sdk


DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ.get('SECRET_KEY', None)

if not SECRET_KEY:
    raise Exception('Add SECRET_KEY env variable, example: export SECRET_KEY=123456')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)

if not EMAIL_HOST_PASSWORD:
    raise Exception('Add EMAIL_HOST_PASSWORD env variable, example: export EMAIL_HOST_PASSWORD=123456')


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jobguyir@gmail.com'
EMAIL_USE_TLS = True


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'jgdb',
        'USER': 'jobguy',
        'PASSWORD': 'J0bGUYdB',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# HTTPS

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

#sentry
SENTRY_URL = os.environ.get('SENTRY_URL', None)

if not SENTRY_URL:
    raise Exception('Add SENTRY_URL env variable, example: export SENTRY_URL='
                    'https://some-id@other-id.ingest.sentry.io/last-id')
sentry_sdk.init(
    SENTRY_URL,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)
