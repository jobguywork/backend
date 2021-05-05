from datetime import datetime, timedelta
from django.conf import settings

from utilities.exceptions import CustomException
from review.models import CompanyReview, Interview, ReviewComment, InterviewComment


def check_create_company_review_permission(user, company):
    if user.is_superuser:
        return
    last_review = CompanyReview.objects.filter(company=company, creator=user).last()
    if not last_review:
        return
    elif last_review.created + timedelta(days=90) < datetime.now():
        return
    else:
        raise CustomException(detail='You reviewed before', code=403)


def check_create_interview_permission(user, company):
    if user.is_superuser:
        return
    last_review = Interview.objects.filter(company=company, creator=user).last()
    if not last_review:
        return
    elif last_review.created + timedelta(days=90) < datetime.now():
        return
    else:
        raise CustomException(detail='You interviewed before', code=403)


def check_create_review_comment_permission(user, review):
    if user.is_superuser:
        return
    comment_count = ReviewComment.objects.filter(creator=user, review=review).count()
    if comment_count >= 10:
        raise CustomException(detail='More than 10 comment not allowed.', code=403)
    return


def check_create_interview_comment_permission(user, interview):
    if user.is_superuser:
        return
    comment_count = InterviewComment.objects.filter(creator=user, interview=interview).count()
    if comment_count >= 10:
        raise CustomException(detail='More than 10 comment not allowed.', code=403)
    return


def check_update_permission(instance, validated_data):
    if isinstance(instance, CompanyReview):
        if validated_data.get('title') and len(instance.title)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['title']):
            raise CustomException(detail='No update permission.', code=403)
        if validated_data.get('description') and len(instance.description)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['description']):
            raise CustomException(detail='No update permission.', code=403)
    if isinstance(instance, Interview):
        if validated_data.get('title') and len(instance.title)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['title']):
            raise CustomException(detail='No update permission.', code=403)
        if validated_data.get('description') and len(instance.description)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['description']):
            raise CustomException(detail='No update permission.', code=403)
    if isinstance(instance, InterviewComment):
        if validated_data.get('body') and len(instance.body)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['body']):
            raise CustomException(detail='No update permission.', code=403)
    if isinstance(instance, ReviewComment):
        if validated_data.get('body') and len(instance.body)*settings.UPDATE_LENGTH_PERCENT_PERMISSION > len(validated_data['body']):
            raise CustomException(detail='No update permission.', code=403)
