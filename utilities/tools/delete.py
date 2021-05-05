from django.utils.translation import ugettext as _
from rest_framework import generics

from utilities import permissions
from utilities.responses import SuccessResponse, ErrorResponse
from utilities.exceptions import CustomException
from job.models import Job
from company.models import City, Province, Company, Gallery, Industry, Benefit
from question.models import Question, Answer
from review.models import CompanyReview, Interview


MODELS_HAVE_IS_DELETED = [Job, City, Province, Company, Gallery, Industry, Benefit, Question, Answer,
                          CompanyReview, Interview]


class DeleteView(generics.DestroyAPIView):
    """
    Delete instance
    """
    def delete(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.get(id=id, is_deleted=False)
            permissions.check_delete_permission(request, instance)
            if self.model in MODELS_HAVE_IS_DELETED:
                instance.is_deleted = True
                instance.save()
            else:
                instance.delete()
            data = {}
            return SuccessResponse(data).send()
        except self.model.DoesNotExist as d:
            return ErrorResponse(message=_('Instance does not exist.'), status=404).send()
        except CustomException as c:
            return ErrorResponse(message=c.detail, status=c.status_code).send()
