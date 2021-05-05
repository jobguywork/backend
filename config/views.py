from querystring_parser import parser
from django.utils.translation import gettext as _
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import authentication_classes, permission_classes, schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.permission import StaffPermission
from api.tools.response import HttpErrorResponse, ErrorResponse, HttpSuccessResponse, SuccessResponse
from config.serializer import IntegerConfigSerializer
from config.models import IntegerConfig
from utils import CUSTOM_SCHEMA
from api.tools.utilities import DailyLoginReputationAndUserAPILogger


@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated, DailyLoginReputationAndUserAPILogger, StaffPermission])
@schema(CUSTOM_SCHEMA)
class IntegerConfigView(generics.GenericAPIView):
    """
    post:
        Create Configs

        name

        value

        description
    patch:
        update configs

        name is unique so it will not update

    get:
        List of configs

        support pagination
    """
    serializer_class = IntegerConfigSerializer
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            return HttpSuccessResponse(SuccessResponse(data).to_json(), status=status.HTTP_200_OK).send()
        else:
            message = _('Error in creating Integer config')
            dev_error = serializer.errors
            show_type = settings.MESSAGE_SHOW_TYPE['NONE']
            return HttpErrorResponse(ErrorResponse(message=message, dev_error=dev_error,
                                                   show_type=show_type).to_json(),
                                     status=status.HTTP_400_BAD_REQUEST).send()

    def get(self, request, *args, **kwargs):
        data = IntegerConfigSerializer(IntegerConfig.objects.all(), many=True)
        arguments = parser.parse(request.GET.urlencode())

        size = int(arguments.pop('size', 20))
        index = int(arguments.pop('index', 0))
        total = index + size
        count = len(data.data)
        return HttpSuccessResponse(SuccessResponse(data.data[index:total], index=index, total=count).to_json(),
                                   status=status.HTTP_200_OK).send()

    def patch(self, request, *args, **kwargs):
        config = IntegerConfig.objects.get(name=request.data.pop('name'))
        serialize_data = self.get_serializer(config, data=request.data, partial=True)
        if serialize_data.is_valid():
            try:
                serialize_data.save()
            except Exception as e:
                raise e
            config.refresh_from_db()
            data = IntegerConfigSerializer(config)
            return HttpSuccessResponse(SuccessResponse(data.data).to_json(), status=status.HTTP_200_OK).send()
        else:
            dev_error = serialize_data.errors
            message = _('Invalid request.')
            show_type = settings.MESSAGE_SHOW_TYPE['NONE']
            return HttpErrorResponse(ErrorResponse(message=message, dev_error=dev_error,
                                                   show_type=show_type).to_json(),
                                     status=status.HTTP_400_BAD_REQUEST).send()
