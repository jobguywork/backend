from rest_framework import generics
from rest_framework.exceptions import ValidationError

from utilities.exceptions import CustomException
from utilities import responses


class CreateView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        try:
            serialize_data = self.get_serializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                self.perform_create(serialize_data)
                return responses.SuccessResponse(serialize_data.data).send()
        except CustomException as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
