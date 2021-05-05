import os

from django.core.validators import RegexValidator
from django.db import transaction
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework import serializers

from authnz.models import Profile
from utilities import utilities


phone_regex = RegexValidator(regex=r'^\d{10}$',
                             message=_('Phone number must be entered in the format:'
                                       " '9137866088'. 10 digits allowed."))


def check_file_exist(path):
    if not path.startswith('~/media/'):
        raise serializers.ValidationError(_('Path must start with ~/media/'))
    if not os.path.isfile(settings.STATIC_ROOT + path[1:]):
        raise serializers.ValidationError(_('File does not exist'))


class RegisterWithEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50, min_length=5)
    password = serializers.CharField(min_length=8, max_length=30)

    def validate_password(self, password):
        if not any(ch.isdigit() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain digit.'))
        if not any(ch.isalpha() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain alpha.'))
        return password


class LoginEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50, min_length=5)
    password = serializers.CharField(min_length=8, max_length=30)


class ChangePassworSerialzier(serializers.Serializer):
    old_password = serializers.CharField(max_length=30, min_length=5)
    password = serializers.CharField(min_length=8, max_length=30)

    def validate_password(self, password):
        if not any(ch.isdigit() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain digit.'))
        if not any(ch.isalpha() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain alpha.'))
        return password


class NickNameSerializer(serializers.Serializer):
    nick_name = serializers.SlugField(max_length=150)


class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3, max_length=30, required=False)
    last_name = serializers.CharField(min_length=3, max_length=30, required=False)
    profile_image = serializers.CharField(max_length=200, required=False, validators=[utilities.check_file_exist])
    facebook = serializers.ReadOnlyField()
    linkedin = serializers.ReadOnlyField()
    twitter = serializers.ReadOnlyField()
    nick_name = serializers.SlugField(max_length=150)
    biography = serializers.CharField(max_length=2000, min_length=10, required=False)
    admin_of_company = serializers.ReadOnlyField()

    @transaction.atomic
    def update(self, instance, validated_data):
        nick_name = validated_data.get('nick_name')
        if nick_name and instance.profile.nick_name != nick_name:
            if Profile.objects.filter(nick_name=validated_data.get('nick_name')):
                raise utilities.exceptions.CustomException(_('This nick name exist.'), code=400)
            instance.profile.nick_name = nick_name
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.profile.profile_image = validated_data.get('profile_image', instance.profile.profile_image)
        instance.profile.biography = validated_data.get('biography', instance.profile.biography)
        instance.save()
        return instance

    def to_representation(self, instance):
        instance.profile_image = instance.profile.profile_image
        instance.facebook = instance.profile.facebook
        instance.linkedin = instance.profile.linkedin
        instance.twitter = instance.profile.twitter
        instance.nick_name = instance.profile.nick_name
        instance.biography = instance.profile.biography
        company = instance.company_set.all()
        if company:
            company = company[0].company_slug
        else:
            company = None
        instance.admin_of_company = company
        instance = super().to_representation(instance)
        return instance


class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)


class ChangePasswordWithForgotTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(min_length=8, max_length=30)
    token = serializers.CharField(min_length=8, max_length=8)

    def validate_password(self, password):
        if not any(ch.isdigit() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain digit.'))
        if not any(ch.isalpha() for ch in password):
            raise exceptions.ValidationError(detail=_('Password must contain alpha.'))
        return password


class SocialTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=2000)
