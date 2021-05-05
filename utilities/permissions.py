from datetime import datetime, timedelta

from django.utils.translation import ugettext as _
from django.core.cache import cache
from django.conf import settings
from rest_framework import permissions

from utilities.exceptions import CustomException
from company.models import Company
from question.models import Question, Answer
from review.models import CompanyReview, Interview, ReviewComment, InterviewComment


class SuperUserPermission(permissions.BasePermission):
    """
    Global permission Super user
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False


def check_perm_owner_update(request, instance):
    if request.user.is_superuser:
        return True
    if isinstance(instance, Company) and instance.user == request.user:
        return True
    elif isinstance(instance, Question) and instance.creator == request.user:
        return True
    elif isinstance(instance, Answer) and instance.creator == request.user:
        return True
    elif isinstance(instance, CompanyReview) and instance.creator == request.user:
        check_has_time_update_permission(instance)
        return True
    elif isinstance(instance, Interview) and instance.creator == request.user:
        check_has_time_update_permission(instance)
        return True
    elif isinstance(instance, ReviewComment) and instance.creator == request.user:
        check_has_time_update_permission(instance)
        return True
    elif isinstance(instance, InterviewComment) and instance.creator == request.user:
        check_has_time_update_permission(instance)
        return True
    else:
        raise CustomException(detail=_('No Permission to update, not yours'), code=403)


def check_has_time_update_permission(instance):
    if instance.created + timedelta(seconds=settings.UPDATE_PERMISSION_DELTA) > datetime.now():
        return True
    else:
        raise CustomException(detail=_('No Permission to update, time expired'), code=403)


def check_delete_permission(request, instance):
    if request.user.is_superuser:
        return True
    elif isinstance(instance, Question) and instance.creator == request.user:
        return True
    elif isinstance(instance, Answer) and instance.creator == request.user:
        return True
    elif isinstance(instance, CompanyReview) and instance.creator == request.user:
        return True
    elif isinstance(instance, Interview) and instance.creator == request.user:
        return True
    elif isinstance(instance, ReviewComment) and instance.creator == request.user:
        return True
    elif isinstance(instance, InterviewComment) and instance.creator == request.user:
        return True
    else:
        raise CustomException(detail=_('No Permission to delete'), code=403)


def check_send_email_permission(email):
    email_count = cache.get('{}{}'.format(settings.EMAIL_SEND_COUNT, email), 0)
    if email_count >= settings.MAX_EMAIL_SEND_COUNT:
        raise CustomException(detail=_('Max email send reached'), code=403)
    else:
        cache.set('{}{}'.format(settings.EMAIL_SEND_COUNT, email), email_count+1,
                  timeout=settings.MAX_EMAIL_SEND_TIMEOUT)


def pagination_permission(user, size, index, allowed_size=50):
    if user.is_staff:
        return size, index
    else:
        return size if size < allowed_size else allowed_size, index


def check_perm_company_owner_update(request, instance):
    if request.user.is_superuser:
        return True
    if request.user == instance.company.user:
        return True
    raise CustomException(detail=_('No Permission to delete'), code=403)
