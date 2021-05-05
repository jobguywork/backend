"""
main response handler, some of response handel throw  middleware
"""
import time
import json

from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _


class BaseResponse:
    def send(self):
        status = self.__dict__.pop('status')
        return HttpResponse(
            json.dumps(self.__dict__),
            status=status,
            content_type="application/json"
        )


class ErrorResponse(BaseResponse):
    def __init__(self, message, dev_error=None, errors=None, show_type=settings.MESSAGE_SHOW_TYPE['TOAST'], status=400):
        self.message = message
        self.dev_error = dev_error
        self.errors = errors
        self.show_type = show_type
        self.current_time = round(time.time())
        self.success = False
        self.status = status


class SuccessResponse(BaseResponse):
    def __init__(self, data=None, message=None, show_type=settings.MESSAGE_SHOW_TYPE['TOAST'], status=200, **kwargs):
        self.data = data
        self.message = message
        self.show_type = show_type
        self.current_time = round(time.time())
        self.success = True
        self.index = kwargs['index'] if kwargs.get('index') is not None else None
        self.total = kwargs['total'] if kwargs.get('total') is not None else None
        self.status = status


class ExceptionHandlerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    @staticmethod
    def process_template_response(request, response):
        if response.status_code == 200 and hasattr(response, 'data') and isinstance(response.data, dict):
            # Ok
            data = response.data
            response.data = {'success': True, 'code': response.status_code, 'index': None, 'total': None,
                             'current_time': round(time.time()), 'message': None,
                             'show_type': settings.MESSAGE_SHOW_TYPE['NONE'], 'data': data}
            # response.data.update(data)

        elif response.status_code == 204:
            # No content it will never return data!!! because of 204
            data = response.data
            response.data = {'success': True, 'code': response.status_code,
                             'current_time': round(time.time()), 'show_type': settings.MESSAGE_SHOW_TYPE['NONE']}
            response.data.update(data)

        elif response.status_code == 403:
            # Forbidden
            data = {
                'errors': response.data,
                'dev_error': {
                    'user': request.user.username, 'api': request.path
                    }
            }

            response.data = {'success': False, 'message': 'Permission denied', 'code': response.status_code,
                             'dev_error': None, 'current_time': round(time.time()), 'errors': None,
                             'show_type': settings.MESSAGE_SHOW_TYPE['TOAST']}

        elif response.status_code == 401:
            # Unauthorized
            data = {'errors': response.data['detail'] if 'detail' in response.data else response.data,
                    'dev_error': {'user_ip': request.META['REMOTE_ADDR'], 'api_address': request.path},
                    'message': 'Unauthorized access.', 'show_type': settings.MESSAGE_SHOW_TYPE['TOAST']}

            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)

        elif response.status_code == 405:
            # Method Not Allowed
            data = {
                'errors': response.data,
                'dev_error': {'user': request.user.username, 'api': request.path},
                'message': 'Method not allowed', 'show_type': settings.MESSAGE_SHOW_TYPE['NONE']
            }

            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)
        elif response.status_code == 406:
            # 406 Not Acceptable
            data = {
                'errors': response.data, 'message': _('Not Acceptable request, maybe not supported version'),
                'dev_error': {'user': request.user.username, 'api': request.path},
                'show_type': settings.MESSAGE_SHOW_TYPE['NONE']
            }

            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)
        elif response.status_code == 415:
            # 415 Unsupported media type
            data = {
                'errors': response.data, 'message': _('Unsupported media type'),
                'dev_error': {'user': request.user.username, 'api': request.path},
                'show_type': settings.MESSAGE_SHOW_TYPE['NONE']
            }

            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)
        elif response.status_code == 400:
            # Bad Request
            error = response.data.pop('dev_error') if 'dev_error' in response.data else None
            data = {
                'errors': response.data['non_field_errors'] if 'non_field_errors' in response.data else response.data,
                'dev_error': {'user': request.user.username, 'api_address': request.path,
                              'user_ip': request.META['REMOTE_ADDR'], 'error': error},
                'message': 'Bad request', 'show_type': settings.MESSAGE_SHOW_TYPE['NONE']
            }
            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)
        elif response.status_code == 429:
            data = {
                'message': response.data['detail'],
                'dev_error': {'user': request.user.username, 'api': request.path},
                'show_type': settings.MESSAGE_SHOW_TYPE['NONE']
            }

            response.data = {'success': False, 'code': response.status_code,
                             'current_time': round(time.time())}
            response.data.update(data)

        return response


def handler404(request, exception):
    message = 'Not found'
    dev_error = 'Not found path {}'.format(request.path)
    show_type = settings.MESSAGE_SHOW_TYPE['NONE']
    return ErrorResponse(message=message, dev_error=dev_error, show_type=show_type, status=404).send()


def handler500(request):
    message = 'Server error'
    show_type = settings.MESSAGE_SHOW_TYPE['NONE']
    return ErrorResponse(message=message, show_type=show_type, status=500).send()
