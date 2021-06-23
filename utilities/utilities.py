import coreapi
import magic
import string
import random
import requests
import re
import uuid
from datetime import timedelta

from django.core.validators import EmailValidator, ValidationError
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import six
from django.utils.translation import ugettext as _
from rest_framework.schemas import AutoSchema
from rest_framework import serializers

from utilities import exceptions
from config.utilities import get_int_config_value


def jwt_response_payload_handler(token, user):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}). data
        }

    """
    company = user.company_set.all()
    if company:
        company = {'company_slug': company[0].company_slug, 'id': company[0].id}
    else:
        company = None
    return {
        'token': token,
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.profile.email,
            'email_confirmed': user.profile.email_confirmed,
            'user_name': user.username,
            'nick_name': user.profile.nick_name,
            'profile_image': user.profile.profile_image,
            'admin_of_company': company,
        },
    }


def forgot_password_delete_account_token_generator():
    all_char = string.digits + string.ascii_uppercase
    return "".join(random.choice(all_char) for x in range(random.randint(8, 8)))


def check_email_or_username(email_username):
    validator = EmailValidator()
    try:
        validator(email_username)
        return settings.EMAIL_USERNAME['EMAIL']
    except ValidationError:
        return settings.EMAIL_USERNAME['USERNAME']


def jwt_get_secret_key(user):
    """
    Use this in generating and checking JWT token,
    and when logout jwt_secret will change so previous JWT token wil be invalidate
    :param user:
    :return:
    """
    return user.profile.jwt_secret


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Email verification code
    """
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.profile.email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()


def send_email_confirm(user, request):
    current_site = get_current_site(request)
    subject = 'تایید عضویت JobGuy'
    message = render_to_string('email_confirm.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })
    resp = send_mail(subject=subject, message='', from_email=None, recipient_list=[user.email], html_message=message)


def send_password_forget_token_email(user, request, forgot_password_token):
    current_site = get_current_site(request)
    subject = 'فراموشی رمز عبور'
    message = render_to_string('forgot_password_token.html', {
        'user_name': user.first_name + ' ' + user.last_name,
        'domain': current_site.domain,
        'token': forgot_password_token,
    })
    send_mail(subject=subject, message='', from_email=None, recipient_list=[user.email], html_message=message)


def check_file_exist(path):
    resp = requests.post('https://upload.jobguy.work/validate/', json={'path': path})
    if resp.status_code == 404:
        raise serializers.ValidationError(_('File does not exist'))
    elif resp.status_code == 200:
        return
    else:
        raise serializers.ValidationError(_('There is an error with media server connection...'))


CUSTOM_PAGINATION_SCHEMA = AutoSchema(manual_fields=[
    coreapi.Field("index", required=False, location="query", type="integer", description="pagination index"),
    coreapi.Field("size", required=False, location="query", type="integer", description="pagination size"),
    coreapi.Field("order_by", required=False, location="query", type="string", description="sort list"),
])



# custom schema used in swgger to add custom field
CUSTOM_UPLOAD_SCHEMA = AutoSchema(manual_fields=[
    coreapi.Field("file", required=False, location="form", type="file", description="upload file")])


def slug_helper(text):
    return '-'.join(re.findall('[\w-]+', text)).lower()


def is_slug(text):
    slugged_text = slug_helper(text)
    if slugged_text == text:
        return True
    else:
        return False


def check_slug_available(model, key, slug_base):
    data = {key: slug_base}
    i = 0
    while model.objects.filter(**data):
        i += 1
        data = {key: slug_base + '_{}'.format(i)}
    if i == 0:
        return slug_base
    else:
        return slug_base + '_{}'.format(i)


def file_uploader(user_uid, path):
    if path:
        resp = requests.post('https://upload.jobguy.work/download/', json={'url': path, 'uid': user_uid})
        if resp.status_code == 200:
            return resp.json()['path']
        else:
            raise serializers.ValidationError(_('There is an error with media server connection...'))
    else:
        return '/user/2e8d9375bbdb401e46d2251c71752b10/image_2019_3_2_11_914343084.jpeg'


def file_check_name(user_name, file, slug):
    file.seek(0)
    file_mime = magic.from_buffer(file.read(), mime=True)
    file.seek(0)
    file_data = {
        'uploadfile': (''.join(file.name.split('.')[:-1]), file.read(), file_mime),
    }
    data = {
        'slug': slug,
        'token': settings.MEDIA_UPLOAD_TOKEN,
    }
    resp = requests.post(settings.MEDIA_UPLOAD_PATH, files=file_data, data=data)
    if resp.status_code == 200:
        return resp.json()['path']
    raise serializers.ValidationError(_('There is an error with media server connection...'))


def telegram_notify(content, id=None, type=None, title=None, body=None):
    try:

        resp = requests.post('https://bot.jobguy.work/api/message', headers={'token': settings.TELEGRAM_BOT_TOKEN},
                             json={'content': content, 'id': id, 'type': type, 'title': title,
                                   'body': body})
    except Exception as e:
        pass


def telegram_notify_channel(content):
    try:
        resp = requests.post('https://bot.jobguy.work/api/public/message',
                             headers={'token': settings.TELEGRAM_BOT_TOKEN}, json={'content': content})
    except Exception as e:
        pass


def uuid_str():
    return ''.join(str(uuid.uuid4()).split('-'))


def check_vote_status(instance, user):
    if user in instance.vote.all():
        return 'UP'
    elif user in instance.down_vote.all():
        return 'DOWN'
    else:
        return 'NONE'


def get_client_ip(request):
    """
    get client ip from request
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def back_months_by_3(publish_time, end_time):
    for i in range(8, 0, -1):
        start_time_period = end_time - timedelta(days=i*90)
        start_time_period2 = end_time - timedelta(days=(i-1)*90)
        if start_time_period <= publish_time < start_time_period2:
            return i


def avg_by_key(lis, key):
    count = len(lis)
    sum = 0
    for item in lis:
        sum += item[key]
    return count, round((sum/count)/1000000, 1)
