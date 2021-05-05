from django.utils.translation import ugettext as _
from rest_framework import exceptions


class CustomException(exceptions.APIException):
    status_code = 400
    default_detail = _('Operation failed.')
    default_code = 'Operation failed.'

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        if detail:
            self.detail = detail
        if code:
            self.status_code = code
