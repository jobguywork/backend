from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from authnz import serialziers as authnz_serializers
from authnz import transactions
from authnz.models import Profile
from review.serializers import UserCompanyReviewListSerializer, UserInterviewListSerializer
from review.models import CompanyReview, Interview
from utilities import responses, utilities, exceptions as authnz_exceptions,permissions

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


@decorators.authentication_classes([])
@decorators.permission_classes([])
class RegisterWithEmailView(generics.CreateAPIView):
    """
    Register with email and password pass min len is 8 and need alpha and numeric
    """
    serializer_class = authnz_serializers.RegisterWithEmailSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                email = serialized_data.data['email'].lower()
                try:
                    user = User.objects.get(profile__email=email)
                except User.DoesNotExist as e:
                    user = None

                if user and user.profile.email_confirmed:
                    raise authnz_exceptions.CustomException(detail=_('This email is registered before.'))
                elif user:
                    permissions.check_send_email_permission(email)
                    user.set_password(serialized_data.data['password'])
                    user.save()
                    utilities.send_email_confirm(user, request)
                    return responses.SuccessResponse().send()
                else:
                    password = serialized_data.data['password']
                    user = transactions.register_user_with_email_and_password(email, password)
                    utilities.send_email_confirm(user, request)
                    return responses.SuccessResponse(message=_('Check your email box.')).send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class LoginEmailView(generics.CreateAPIView):
    """
    Login with email and pass
    """
    serializer_class = authnz_serializers.LoginEmailSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                email = serialized_data.data['email'].lower()
                try:
                    user = User.objects.get(profile__email=email, profile__email_confirmed=True)
                except User.DoesNotExist:
                    raise authnz_exceptions.CustomException(detail=_('Email is invalid or not confirmed'))

                if user.check_password(serialized_data.data['password']):
                    if user.is_active:
                        payload = jwt_payload_handler(user)  # todo: Is deprecated
                        jwt_token = utilities.jwt_response_payload_handler(jwt_encode_handler(payload), user=user)
                        return responses.SuccessResponse(jwt_token).send()
                    else:
                        raise authnz_exceptions.CustomException(detail=_('This user is inactive, contact us.'))
                else:
                    raise authnz_exceptions.CustomException(detail=_('Email or Password is invalid.'))
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class ChangePasswordView(generics.CreateAPIView):
    """
    Change pass min len 5 and max is 30  and need alpha and numeric
    """
    serializer_class = authnz_serializers.ChangePassworSerialzier
    throttle_classes = []

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                if request.user.check_password(serialized_data.data['old_password']):
                    if request.user.is_active:
                        transactions.change_user_password(request.user, serialized_data.data['password'])
                        payload = jwt_payload_handler(request.user)  # todo: Is deprecated
                        jwt_token = utilities.jwt_response_payload_handler(jwt_encode_handler(payload),
                                                                           user=request.user)
                        return responses.SuccessResponse(jwt_token).send()
                    else:
                        raise authnz_exceptions.CustomException(detail=_('This user is deactivated, contact us.'))
                else:
                    raise authnz_exceptions.CustomException(detail=_('Old Password is invalid.'))
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RefreshTokenView(generics.RetrieveAPIView):
    """
    Refresh JWT token
    """
    throttle_classes = []

    def get(self, request):
        try:
            if request.user.is_active:
                payload = jwt_payload_handler(request.user)  # todo: Is deprecated
                jwt_token = utilities.jwt_response_payload_handler(jwt_encode_handler(payload),
                                                                   user=request.user)
                return responses.SuccessResponse(jwt_token).send()
            else:
                raise authnz_exceptions.CustomException(detail=_('This user is inactive, contact us.'))

        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class NickNameAvailabilityView(generics.CreateAPIView):
    """
    Check nick name exist or not
    """
    serializer_class = authnz_serializers.NickNameSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                nick_name = serialized_data.data['nick_name']
                if request.user.profile.nick_name == nick_name:
                    return responses.SuccessResponse().send()
                if Profile.objects.filter(nick_name__iexact=nick_name):
                    raise authnz_exceptions.CustomException(detail=_('This nick name exists'))
                else:
                    return responses.SuccessResponse().send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class UpdateUserProfileView(generics.UpdateAPIView):
    """
    Update user profile

    upload user profile image in upload api and set returned path here in profile image
    """
    serializer_class = authnz_serializers.UserSerializer
    model = User
    throttle_classes = []

    def patch(self, request):
        try:
            serialize_data = self.get_serializer(request.user, data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                try:
                    self.perform_update(serialize_data)
                except Exception as e:
                    raise e
                serialize_data = self.get_serializer(request.user)
                return responses.SuccessResponse(serialize_data.data).send()

        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()

    def put(self, request):
        try:
            serialize_data = self.get_serializer(request.user, data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                try:
                    self.perform_update(serialize_data)
                except Exception as e:
                    raise e
                serialize_data = self.get_serializer(request.user)
                return responses.SuccessResponse(serialize_data.data).send()

        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class ConfirmEmailView(generics.RetrieveAPIView):
    """
    Confirm email link will call from email
    """
    throttle_classes = []

    def get(self, request, uidb64, token):
        try:
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and utilities.account_activation_token.check_token(user, token):
                user.profile.email_confirmed = True
                user.profile.save()
                return render(request, 'mail_confirmed.html', {'domain': get_current_site(request).domain,
                                                               'name': user.username})
            else:
                return render(request, 'mail_confirm_invalid.html', {'domain': get_current_site(request).domain})

        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class ForgotPasswordEmailView(generics.CreateAPIView):
    """
    Send forgot password token to email

    email max len is 50
    """
    serializer_class = authnz_serializers.ForgotPasswordEmailSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialize_data = self.serializer_class(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                email = serialize_data.data['email'].lower()
                try:
                    user = User.objects.get(profile__email=email)
                except User.DoesNotExist:
                    raise authnz_exceptions.CustomException(detail=_('Email does not exist.'))
                if user.is_active and user.email:
                    forgot_password_token = cache.get('{}{}'.format(user.username,
                                                                    settings.CACHE_FORGOT_PASSWORD_TOKEN))
                    if not forgot_password_token:
                        permissions.check_send_email_permission(email)
                        forgot_password_token = utilities.forgot_password_delete_account_token_generator()
                        utilities.send_password_forget_token_email(user, request, forgot_password_token)
                        cache.set('{}{}'.format(user.username, settings.CACHE_FORGOT_PASSWORD_TOKEN),
                                  forgot_password_token, timeout=settings.TIMEOUT_FORGOT_PASSWORD_TOKEN)
                        return responses.SuccessResponse(message=_('Check Your email for token.')).send()
                    else:
                        raise authnz_exceptions.CustomException(detail=_('We sent an token recently please try later'))
                elif not user.is_active:
                    raise authnz_exceptions.CustomException(detail=_('This account is inactive.'))
                else:
                    raise authnz_exceptions.CustomException(detail=_('This account has no email.'))

        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class ChangePasswordWithForgotTokenView(generics.CreateAPIView):
    """
    Change password with forgot token
    """
    serializer_class = authnz_serializers.ChangePasswordWithForgotTokenSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialize_data = self.serializer_class(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                email = serialize_data.data['email'].lower()
                try:
                    user = User.objects.get(profile__email=email)
                except User.DoesNotExist:
                    raise authnz_exceptions.CustomException(detail=_('Email does not exist.'))

                if user.is_active:
                    forgot_password_token = cache.get('{}{}'.format(user.username,
                                                                    settings.CACHE_FORGOT_PASSWORD_TOKEN))
                    if forgot_password_token == serialize_data.data['token']:
                        transactions.change_user_password(user, serialize_data.data['password'])
                        cache.delete('{}{}'.format(user.username, settings.CACHE_FORGOT_PASSWORD_TOKEN))
                        payload = jwt_payload_handler(user)  # todo: Is deprecated
                        jwt_token = utilities.jwt_response_payload_handler(jwt_encode_handler(payload),
                                                                           user=user)
                        return responses.SuccessResponse(jwt_token).send()
                    elif not forgot_password_token:
                        raise authnz_exceptions.CustomException(detail=_('Token timeout.'))
                    else:
                        raise authnz_exceptions.CustomException(detail=_('We sent a new token recently please try it.'))
                else:
                    raise authnz_exceptions.CustomException(detail=_('Your account is inactive.'))
        except exceptions.ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class SocialTokenView(generics.GenericAPIView):
    """
    post:
        backend     google

        token  token for open auth
    """
    serializer_class = authnz_serializers.SocialTokenSerializer
    throttle_classes = []

    @transaction.atomic
    def post(self, request, backend, *args, **kwargs):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                token = serialized_data.data['token']
                if backend.lower() == 'google':
                    try:
                        resp_user = id_token.verify_oauth2_token(token, google_requests.Request(),
                                                                 settings.GOOGLE_OAUTH_ID)
                    except Exception as e:
                        return responses.ErrorResponse(message='Error in google open auth',
                                                       dev_error=str(e), status=400).send()
                    if resp_user['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                        raise authnz_exceptions.CustomException(detail=_('Google Wrong issuer.'))
                    if not resp_user.get('email') or not resp_user.get('given_name') or \
                            not resp_user.get('family_name') or not resp_user.get('picture'):
                        raise authnz_exceptions.CustomException(
                            detail=_('Scope need to have email, given name, family, picture'))
                    email = resp_user['email'].lower()
                    try:
                        user = User.objects.get(profile__email=email)
                    except User.DoesNotExist as e:
                        user = transactions.open_auth_user_creator(email, resp_user['given_name'],
                                                                   resp_user['family_name'], resp_user['picture'])
                else:
                    raise authnz_exceptions.CustomException(detail=_('Wrong backend'))
            if user.is_active:
                payload = jwt_payload_handler(user)  # todo: Is deprecated
                jwt_token = utilities.jwt_response_payload_handler(jwt_encode_handler(payload), user=user)
            else:
                raise authnz_exceptions.CustomException(
                            detail=_('Your user account is deactivated, contact us for more information.'))
            return responses.SuccessResponse(jwt_token).send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class SetSocialTokenView(generics.GenericAPIView):
    """
    post:
        set email to mobile registered

        backend     google

        token  token for open auth
    """
    serializer_class = authnz_serializers.SocialTokenSerializer
    throttle_classes = []

    @transaction.atomic
    def post(self, request, backend, *args, **kwargs):
        try:
            if request.user.profile.email and request.user.profile.email_confirmed:
                return responses.ErrorResponse(message=_('This email used before.')).send()
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                token = serialized_data.data['token']
                if backend.lower() == 'google':
                    try:
                        resp_user = id_token.verify_oauth2_token(token, google_requests.Request(),
                                                                 settings.GOOGLE_OAUTH_ID)
                    except Exception as e:
                        return responses.ErrorResponse(message='Error in google open auth',
                                                       dev_error=str(e), status=400).send()
                    if resp_user['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                        raise authnz_exceptions.CustomException(detail=_('Google Wrong issuer.'))
                    if not resp_user.get('email') or not resp_user.get('given_name') or \
                            not resp_user.get('family_name') or not resp_user.get('picture'):
                        raise authnz_exceptions.CustomException(
                            detail=_('Scope need to have email, given name, family, picture'))
                    email = resp_user['email'].lower()
                    try:
                        user = User.objects.get(profile__email=email)
                    except User.DoesNotExist as e:
                        user = None
                    if user:
                        raise authnz_exceptions.CustomException(detail=_('This email was used before.'))
                    else:
                        request.user.profile.email = email
                        request.user.profile.email_confirmed = True
                        request.user.save()
                else:
                    raise authnz_exceptions.CustomException(detail=_('Wrong backend'))
            return responses.SuccessResponse().send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class MyReviewListView(generics.ListAPIView):
    """
    get:

        list of my reviews
    """
    serializer_class = UserCompanyReviewListSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            company_review_list = self.model.objects.filter(creator=request.user)
            data = self.get_serializer(company_review_list, many=True)
            return responses.SuccessResponse(data.data).send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class MyInterviewListView(generics.ListAPIView):
    """
    get:

        list of my interviews
    """
    serializer_class = UserInterviewListSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            interview_list = self.model.objects.filter(creator=request.user)
            data = self.get_serializer(interview_list, many=True)
            return responses.SuccessResponse(data.data).send()
        except authnz_exceptions.CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
