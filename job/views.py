from rest_framework import decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utilities.tools import create, delete, list_result, update
from utilities.utilities import CUSTOM_PAGINATION_SCHEMA
from utilities import permissions
from job.models import Job
from job.serializers import JobSerializer, PublicJobSerializer


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class JobCreateView(create.CreateView):
    """
    name Required
    """
    serializer_class = JobSerializer
    model = Job
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class JobListView(list_result.ListView):
    serializer_class = JobSerializer
    model = Job
    throttle_classes = []


@decorators.authentication_classes([])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserJobListView(list_result.UserListView):
    serializer_class = PublicJobSerializer
    model = Job
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class JobUpdateView(update.UpdateView):
    serializer_class = JobSerializer
    model = Job
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class JobDeleteView(delete.DeleteView):
    serializer_class = JobSerializer
    model = Job
    throttle_classes = []
