from hashlib import md5
from time import time

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

from utilities.utilities import uuid_str


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    jwt_secret = models.CharField(max_length=32, default=uuid_str)
    mobile = models.CharField(max_length=10, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    profile_image = models.CharField(max_length=200, null=True)
    email_confirmed = models.BooleanField(default=False)
    mobile_confirmed = models.BooleanField(default=False)
    facebook = models.CharField(max_length=200, null=True, blank=True)
    linkedin = models.CharField(max_length=200, null=True, blank=True)
    twitter = models.CharField(max_length=200, null=True, blank=True)
    biography = models.CharField(max_length=2000, null=True, blank=True)
    nick_name = models.SlugField(max_length=255, null=True, unique=True)
    total_review = models.IntegerField(default=0)
    rate_avg = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.nick_name is None:
            nick_name = md5(str(time()).encode())
            nick_name.update(self.user.username.encode())
            self.nick_name = nick_name.hexdigest()
        super().save(*args, **kwargs)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            cache.delete(settings.TOTAL_USER)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def hash_user_data(self):
        if self.email:
            self.email = md5(self.email.encode()).hexdigest()[:30]
        if self.mobile:
            self.mobile = md5(self.mobile.encode()).hexdigest()[:10]
        if self.user.first_name:
            self.user.first_name = md5(self.user.first_name.encode()).hexdigest()[:30]
        if self.user.last_name:
            self.user.last_name = md5(self.user.last_name.encode()).hexdigest()[:30]
        if self.user.email:
            self.user.email = md5(self.user.email.encode()).hexdigest()[:30]
        self.user.username = md5(self.user.username.encode()).hexdigest()[:30]
        self.save()
        self.user.profile.jwt_secret = uuid_str()
        self.user.save()
