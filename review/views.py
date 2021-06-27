from querystring_parser import parser
from django.conf import settings
from django.core.cache import cache
from rest_framework import decorators, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.throttling import UserRateThrottle

from question.models import Answer, Question
from review.models import Pros, Cons, CompanyReview, Interview, ReviewComment, InterviewComment
from review.serializers import (ProsSerializer, UserProsSerializer, ConsSerializer, UserConsSerializer,
                                CompanyReviewSerializer, UserCompanyReviewSerializer, InterviewSerializer,
                                UserInterviewSerializer, ReviewCommentSerializer, UserReviewCommentSerializer,
                                InterviewCommentSerializer, BotApproveReviewSerializer, ReplyCompanyReviewSerializer,
                                ReplyInterviewSerializer)
from review.utilities import (check_notify_to_telegram_channel, get_compnay,
                              send_notice_instance_rejected)
from utilities import responses, utilities
from utilities.exceptions import CustomException
from utilities.tools import create, delete, list_result, update, retrieve
from utilities.utilities import CUSTOM_PAGINATION_SCHEMA
from utilities import permissions

# Pros
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProsCreateView(create.CreateView):
    """
    name Required
    """
    serializer_class = ProsSerializer
    model = Pros
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class ProsListView(list_result.ListView):
    serializer_class = ProsSerializer
    model = Pros
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserProsListView(list_result.UserListView):
    serializer_class = UserProsSerializer
    model = Pros
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProsUpdateView(update.UpdateView):
    serializer_class = ProsSerializer
    model = Pros
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProsDeleteView(delete.DeleteView):
    serializer_class = ProsSerializer
    model = Pros
    throttle_classes = []


# Cons
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ConsCreateView(create.CreateView):
    """
    name Required
    """
    serializer_class = ConsSerializer
    model = Cons
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class ConsListView(list_result.ListView):
    serializer_class = ConsSerializer
    model = Cons
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserConsListView(list_result.UserListView):
    serializer_class = UserConsSerializer
    model = Cons
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ConsUpdateView(update.UpdateView):
    serializer_class = ConsSerializer
    model = Cons
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ConsDeleteView(delete.DeleteView):
    serializer_class = ConsSerializer
    model = Cons
    throttle_classes = []


# Company Review
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyReviewCreateView(create.CreateView):
    """
    company object company_slug is required

    job object name is required

    pros & cons list object object of name is required

    state FULL, PART, CONTRACT, INTERN, FREELANCE

    work_life_balance 1-5

    salary_benefit 1-5

    security 1-5

    management 1-5

    culture 1-5

    title max 100

    description max 40000, required False

    salary_per_month int field  YEAR, MONTH, DAY, HOUR
    """
    serializer_class = CompanyReviewSerializer
    model = CompanyReview
    throttle_classes = [UserRateThrottle]


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyReviewListView(list_result.ListView):
    serializer_class = CompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserCompanyReviewListView(list_result.UserListView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
class UserCompanyReviewRetrieveView(retrieve.RetrieveView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AdminCompanyReviewRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            if instance.approved or request.user == instance.company.user:
                instance.view.add(request.user)
                serialize_data = self.get_serializer(instance)
                return responses.SuccessResponse(serialize_data.data).send()
            else:
                return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyReviewUpdateView(update.UpdateView):
    serializer_class = CompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CompanyReviewDeleteView(delete.DeleteView):
    serializer_class = CompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteCompanyReviewView(generics.RetrieveAPIView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.down_vote.all():
                instance.down_vote.remove(request.user)
            instance.vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyReviewReplyView(generics.UpdateAPIView):
    serializer_class = ReplyCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def put(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            permissions.check_perm_company_owner_update(request, instance)
            serialize_data = self.get_serializer(instance, data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_update(serialize_data)
                data = self.get_serializer(instance)
                return responses.SuccessResponse(data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()
        except CustomException as c:
            return responses.ErrorResponse(message=c.detail, status=c.status_code).send()
        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveVoteCompanyReviewView(generics.RetrieveAPIView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddDownVoteCompanyReviewView(generics.RetrieveAPIView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.vote.all():
                instance.vote.remove(request.user)
            instance.down_vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveDownVoteCompanyReviewView(generics.RetrieveAPIView):
    serializer_class = UserCompanyReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


# Interview
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class InterviewCreateView(create.CreateView):
    """
    company object company_slug is required

    job object name is required

    pros & cons list object object of name is required

    status WORKING, ACCEPT, REJECT, NORESPONSE

    apply_method CO_STAFF, CO_SITE, JOB_SITE, EMAIL, FRIEND, LINKEDIN, FESTIVAL, EVENT, OTHER

    interviewer_rate 1-5

    total_rate 1-5

    interview_date date

    title max 100

    description max 40000, required False

    asked_salary int field

    offered_salary int field

    response_time_before_review 1WEEK, 2WEEK, 1MONT, MORE

    response_time_after_review 1WEEK, 2WEEK, 1MONT, MORE
    """
    serializer_class = InterviewSerializer
    model = Interview
    throttle_classes = [UserRateThrottle]


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class InterviewListView(list_result.ListView):
    serializer_class = InterviewSerializer
    model = Interview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserInterviewListView(list_result.UserListView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
class UserInterviewRetrieveView(retrieve.RetrieveView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AdminInterviewRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            if instance.approved or request.user == instance.company.user:
                instance.view.add(request.user)
                serialize_data = self.get_serializer(instance)
                return responses.SuccessResponse(serialize_data.data).send()
            else:
                return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class InterviewUpdateView(update.UpdateView):
    serializer_class = InterviewSerializer
    model = Interview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class InterviewDeleteView(delete.DeleteView):
    serializer_class = InterviewSerializer
    model = Interview
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyInterReviewReplyView(generics.UpdateAPIView):
    serializer_class = ReplyInterviewSerializer
    model = Interview
    throttle_classes = []

    def put(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            permissions.check_perm_company_owner_update(request, instance)
            serialize_data = self.get_serializer(instance, data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_update(serialize_data)
                data = self.get_serializer(instance)
                return responses.SuccessResponse(data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()
        except CustomException as c:
            return responses.ErrorResponse(message=c.detail, status=c.status_code).send()
        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteInterviewView(generics.RetrieveAPIView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.down_vote.all():
                instance.down_vote.remove(request.user)
            instance.vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveVoteInterviewView(generics.RetrieveAPIView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddDownVoteInterviewView(generics.RetrieveAPIView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.vote.all():
                instance.vote.remove(request.user)
            instance.down_vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveDownVoteInterviewView(generics.RetrieveAPIView):
    serializer_class = UserInterviewSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


# Review comment
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class ReviewCommentCreateView(create.CreateView):
    """
    body max 500

    review {"id": ""}
    """
    serializer_class = ReviewCommentSerializer
    model = ReviewComment
    throttle_classes = [UserRateThrottle]


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class ReviewCommentUpdateView(update.UpdateView):
    """
    body max 500

    """
    serializer_class = ReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class ReviewCommentDeleteView(delete.DeleteView):
    serializer_class = ReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class ReviewCommentListView(generics.ListAPIView):
    """
    List of review comments

    have pagination

    filter and sort is not developed

    sort on vote_count
    """
    serializer_class = UserReviewCommentSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            if not instance.has_legal_issue:
                if not instance.approved:
                    if request.user == instance.creator or (not request.user.is_anonymous and request.user.is_staff):
                        pass
                    else:
                        raise self.model.DoesNotExist
                serialize_data = self.get_serializer(instance.reviewcomment_set.filter(
                    is_deleted=False, approved=True
                ).all(), many=True)
                data = serialize_data.data
                data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            else:
                data = []
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AdminReviewCommentListView(generics.ListAPIView):
    serializer_class = UserReviewCommentSerializer
    model = CompanyReview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            if not instance.approved:
                if request.user == instance.company.user:
                    pass
                else:
                    raise self.model.DoesNotExist
            serialize_data = self.get_serializer(instance.reviewcomment_set.filter(is_deleted=False).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())
            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteReviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.down_vote.all():
                instance.down_vote.remove(request.user)
            instance.vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveVoteReviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddDownVoteReviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.vote.all():
                instance.vote.remove(request.user)
            instance.down_vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveDownVoteReviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = ReviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


# Interview comment
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class InterviewCommentCreateView(create.CreateView):
    """
    body max 500

    interview {"id": ""}
    """
    serializer_class = InterviewCommentSerializer
    model = InterviewComment
    throttle_classes = [UserRateThrottle]


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class InterviewCommentUpdateView(update.UpdateView):
    """
    body max 500

    """
    serializer_class = InterviewCommentSerializer
    model = InterviewComment
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class InterviewCommentDeleteView(delete.DeleteView):
    serializer_class = InterviewCommentSerializer
    model = InterviewComment
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class InterviewCommentListView(generics.ListAPIView):
    """
    List of interview comments

    have pagination

    filter and sort is not developed

    sort on vote_count
    """
    serializer_class = UserReviewCommentSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())
            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            instance = self.model.objects.get(id=id, is_deleted=False)
            if not instance.has_legal_issue:
                if not instance.approved:
                    if request.user == instance.creator or (not request.user.is_anonymous and request.user.is_staff):
                        pass
                    else:
                        raise self.model.DoesNotExist
                serialize_data = self.get_serializer(instance.interviewcomment_set.filter(
                    is_deleted=False, approved=True
                ).all(), many=True)

                data = serialize_data.data
                data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            else:
                data = []
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AdminInterviewCommentListView(generics.ListAPIView):
    serializer_class = UserReviewCommentSerializer
    model = Interview
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            if not instance.approved:
                if request.user == instance.company.user:
                    pass
                else:
                    raise self.model.DoesNotExist
            serialize_data = self.get_serializer(instance.interviewcomment_set.filter(is_deleted=False).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteInterviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = InterviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.down_vote.all():
                instance.down_vote.remove(request.user)
            instance.vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveVoteInterviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = InterviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddDownVoteInterviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = InterviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            if request.user in instance.vote.all():
                instance.vote.remove(request.user)
            instance.down_vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveDownVoteInterviewCommentView(generics.RetrieveAPIView):
    serializer_class = UserReviewCommentSerializer
    model = InterviewComment
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class BotApproveReviewView(generics.CreateAPIView):
    serializer_class = BotApproveReviewSerializer
    model = CompanyReview
    throttle_classes = []

    def post(self, request):
        try:
            serialize_data = self.get_serializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                if serialize_data.data["key"] == settings.BOT_APPROVE_KEY:
                    instance_map = {
                        "review": CompanyReview,
                        "interview": Interview,
                        "question": Question,
                        "answer": Answer,
                        "review_comment": ReviewComment,
                        "interview_comment": InterviewComment,
                    }
                    if serialize_data.data["type"] in instance_map.keys():
                        try:
                            instance = instance_map[serialize_data.data["type"]].objects.get(
                                id=serialize_data.data["id"]
                            )
                        except (
                                CompanyReview.DoesNotExist, Interview.DoesNotExist,
                                Question.DoesNotExist, Answer.DoesNotExist,
                                ReviewComment.DoesNotExist, InterviewComment.DoesNotExist
                                ) as e:
                            raise CustomException(detail="Instance does not Found.",
                                                  code=404)
                    else:
                        raise CustomException(detail="Instance type does not exist.")
                    instance.approved = serialize_data.data["approved"]
                    instance.save()
                    if serialize_data.data["type"] in ["review", "interview"]:
                        cache.delete(settings.LAST_REVIEWS)
                        cache.delete(settings.LAST_INTERVIEWS)
                        if check_notify_to_telegram_channel(serialize_data.data):
                            if serialize_data.data["type"] == "review":
                                review_link = "{}/review/{}".format(settings.WEB_BASE_PATH, instance.id)
                                utilities.telegram_notify_channel(
                                    "تجربه کاری {} در {}, را در جابگای بخوانید. \n {} \n {} \n {}".format(
                                        instance.title, instance.company.name, review_link,
                                        "#" + instance.company.city.city_slug, "#review"))
                                instance.company.handle_company_review_statics()
                            elif serialize_data.data["type"] == "interview":
                                review_link = "{}/interview/{}".format(settings.WEB_BASE_PATH, instance.id)
                                utilities.telegram_notify_channel(
                                    "تجربه مصاحبه {} در {}, را در جابگای بخوانید. \n {} \n {} \n {}".format(
                                        instance.title, instance.company.name, review_link,
                                        "#"+instance.company.city.city_slug, "#interview"))
                                instance.company.handle_company_interview_statics()
                    if not instance.approved:
                        instance_type = serialize_data.data["type"]
                        fa_map = {
                            "review": "تجربه کاری",
                            "interview": "تجربه مصاحبه",
                            "question": "سوال",
                            "answer": "پاسخ",
                            "review_comment": "نظر",
                            "interview_comment": "نظر",
                        }
                        company = get_compnay(instance, instance_type)
                        send_notice_instance_rejected(
                            instance.creator, fa_map[instance_type], company
                        )
                    return responses.SuccessResponse().send()
                else:
                    raise CustomException(detail="Instance does not Found.", code=404)
        except CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
