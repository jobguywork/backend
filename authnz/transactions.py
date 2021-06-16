from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings

from utilities import utilities


@transaction.atomic
def register_user_with_email_and_password(email, password):
    user = User(email=email, username=email)
    user.set_password(password)
    user.save()
    user.profile.email = email
    user.save()
    return user


@transaction.atomic
def change_user_password(user, password):
    user.set_password(password)
    user.profile.jwt_secret = utilities.uuid_str()
    user.save()


@transaction.atomic
def open_auth_user_creator(email, first_name, last_name, profile_image):
    user = User(username=email, email=email, first_name=first_name.title(), last_name=last_name.title())
    user.save()
    user.profile.profile_image = utilities.file_uploader(user.profile.nick_name, profile_image)
    user.profile.email = email
    user.profile.email_confirmed = True
    user.save()
    return user
