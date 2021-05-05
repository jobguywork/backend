from django.db import models


class IntegerConfig(models.Model):
    name = models.CharField(verbose_name='Config name', max_length=50, unique=True)
    value = models.IntegerField(verbose_name='Config value')
    description = models.CharField(verbose_name='Config description', max_length=200)

    def __str__(self):
        return self.name
