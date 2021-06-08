from datetime import datetime

from django.core.cache import cache
from django.conf import settings
from django.db import models


class Donate(models.Model):
    LTC = 'LT'
    ONE = 'ON'
    TOMO = 'TO'
    DOGE = 'DG'
    ADA = 'AD'
    TRX = 'TR'
    DOT = 'DT'
    BUST = 'BU'
    USDT = 'US'
    DGB = 'DB'
    ETC = 'ET'
    ETH = 'EH'
    XLM = 'XL'
    QTUM = 'QT'

    COIN_CHOICES = (
        (LTC, 'LTC'),
        (ONE, 'ONE'),
        (TOMO, 'TOMO'),
        (DOGE, 'DOGE'),
        (ADA, 'ADA'),
        (TRX, 'TRX'),
        (DOT, 'DOT'),
        (BUST, 'BUST'),
        (USDT, 'USDT'),
        (DGB, 'DGB'),
        (ETC, 'ETC'),
        (ETH, 'ETH'),
        (XLM, 'XLM'),
        (QTUM, 'QTUM'),
    )
    name = models.CharField(max_length=50)
    amount = models.FloatField()
    created = models.DateTimeField(default=datetime.now)
    coin = models.CharField(choices=COIN_CHOICES, max_length=2)
    is_active = models.BooleanField(default=False)
    link = models.CharField(max_length=500, null=True, blank=True)
    cost = models.FloatField(default=0)

    class Meta:
        ordering = ('-amount',)

    def __str__(self):
        return 'Donate: {} - {} by {}'.format(self.amount, self.coin, self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(settings.DONATE_LIST)
