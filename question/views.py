from django.core.exceptions import FieldError
from django.contrib.auth.models import AnonymousUser
from rest_framework import generics
from rest_framework import decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from querystring_parser import parser

from utilities import responses
from utilities.tools import create, delete, list_result, update
from utilities.utilities import CUSTOM_PAGINATION_SCHEMA
from utilities import permissions
from question.models import Question, Answer
from question.serializers import QuestionSerializer, AnswerSerializer, PublicAnswerSerializer, PublicQuestionSerializer


# Question
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class QuestionCreateView(create.CreateView):
    """
    title max 100 min 5

    body max 1000 min 10
    """
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class QuestionListView(list_result.ListView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserQuestionListView(list_result.UserListView):
    serializer_class = PublicQuestionSerializer
    model = Question
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserQuestionAnswersListView(generics.ListAPIView):
    serializer_class = PublicAnswerSerializer
    model = Question
    throttle_classes = []

    def get(self, request, question_slug, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size

            sort = None
            if arguments.get('order_by'):
                sort = arguments.pop('order_by')

            question = self.model.objects.get(question_slug=question_slug,
                                              is_deleted=False,
                                              approved=True,
                                              )
            if not isinstance(request.user, AnonymousUser):
                question.view.add(request.user)
            question.total_view += 1
            question.save()
            result = question.answer_set
            result = result.filter(is_deleted=False)
            if sort:
                result = result.order_by(sort)
            result = result.all()
            total = len(result)
            result = result[index:size]
            data = self.get_serializer(result, many=True)
            return responses.SuccessResponse(data.data, index=index, total=total).send()
        except FieldError as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class QuestionUpdateView(update.UpdateView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class QuestionDeleteView(delete.DeleteView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []


# Answer
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AnswerCreateView(create.CreateView):
    """
    body max 5000 min 10
    """
    serializer_class = AnswerSerializer
    model = Answer
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AnswerListView(list_result.ListView):
    serializer_class = AnswerSerializer
    model = Answer
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserAnswerListView(list_result.UserListView):
    serializer_class = AnswerSerializer
    model = Answer
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AnswerUpdateView(update.UpdateView):
    serializer_class = AnswerSerializer
    model = Answer
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AnswerDeleteView(delete.DeleteView):
    serializer_class = AnswerSerializer
    model = Answer
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []

    def get(self, request, question_slug, *args, **kwargs):
        try:
            instance = self.model.objects.get(question_slug=question_slug)
            if request.user in instance.down_vote.all():
                instance.down_vote.remove(request.user)
            instance.vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveVoteQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []

    def get(self, request, question_slug, *args, **kwargs):
        try:
            instance = self.model.objects.get(question_slug=question_slug)
            instance.vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddDownVoteQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []

    def get(self, request, question_slug, *args, **kwargs):
        try:
            instance = self.model.objects.get(question_slug=question_slug)
            if request.user in instance.vote.all():
                instance.vote.remove(request.user)
            instance.down_vote.add(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RemoveDownVoteQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    model = Question
    throttle_classes = []

    def get(self, request, question_slug, *args, **kwargs):
        try:
            instance = self.model.objects.get(question_slug=question_slug)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class AddVoteAnswerView(generics.RetrieveAPIView):
    serializer_class = PublicAnswerSerializer
    model = Answer
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
class RemoveVoteAnswerView(generics.RetrieveAPIView):
    serializer_class = PublicAnswerSerializer
    model = Answer
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
class AddDownVoteAnswerView(generics.RetrieveAPIView):
    serializer_class = PublicAnswerSerializer
    model = Answer
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
class RemoveDownVoteAnswerView(generics.RetrieveAPIView):
    serializer_class = PublicAnswerSerializer
    model = Answer
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id)
            instance.down_vote.remove(request.user)
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=400).send()
