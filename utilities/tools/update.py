from django.utils.translation import ugettext as _
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from utilities import permissions
from utilities.responses import SuccessResponse, ErrorResponse
from utilities.exceptions import CustomException


class UpdateView(generics.UpdateAPIView):
    def put(self, request, id, *args, **kwargs):  # need full required parameters
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            permissions.check_perm_owner_update(request, instance)

            serialize_data = self.get_serializer(instance, data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_update(serialize_data)
                data = self.get_serializer(instance)
                return SuccessResponse(data.data).send()
        except self.model.DoesNotExist as d:
            return ErrorResponse(message=_('Instance does not exist.'), status=404).send()
        except CustomException as c:
            return ErrorResponse(message=c.detail, status=c.status_code).send()
        except ValidationError as e:
            return ErrorResponse(message=e.detail, status=e.status_code).send()

    def patch(self, request, id, *args, **kwargs):  # just send parameters you want to update, don't need to send them all
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            permissions.check_perm_owner_update(request, instance)

            serialize_data = self.get_serializer(instance, data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_update(serialize_data)
                data = self.get_serializer(instance)
                return SuccessResponse(data.data).send()
        except self.model.DoesNotExist as d:
            return ErrorResponse(message=_('Instance does not exist.'), status=404).send()
        except CustomException as c:
            return ErrorResponse(message=c.detail, status=c.status_code).send()
        except ValidationError as e:
            return ErrorResponse(message=e.detail, status=e.status_code).send()
