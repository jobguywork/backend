from django.contrib.auth.models import AnonymousUser
from rest_framework import generics

from utilities import responses
from review.models import CompanyReview, Interview
from question.models import Question


class RetrieveView(generics.RetrieveAPIView):

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            if instance.approved or request.user == instance.creator or (not request.user.is_anonymous and request.user.is_staff):
                if self.model in [CompanyReview, Question, Interview]:
                    if not isinstance(request.user, AnonymousUser):  # view of company review, question
                        instance.view.add(request.user)
                    instance.total_view += 1
                    instance.save()
                serialize_data = self.get_serializer(instance)
                return responses.SuccessResponse(serialize_data.data).send()
            else:
                return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
        except self.model.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()
