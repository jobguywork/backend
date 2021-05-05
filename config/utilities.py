from django.core.cache import cache
from django.conf import settings

from config.models import IntegerConfig


def get_int_config_value(config_name):
    value = cache.get('{}{}'.format(settings.INTEGER_CONFIG_CACHE, config_name))
    if not value:
        value = IntegerConfig.objects.get(name=config_name).value
        cache.set('{}{}'.format(settings.INTEGER_CONFIG_CACHE, config_name), value, timeout=24*60*60)
    return value
