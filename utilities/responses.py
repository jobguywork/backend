"""
main response handler, some of response handel throw  middleware
"""
import time

from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework.response import Response


class BaseResponse:
    def __init__(self, **kwargs):
        self.message = kwargs.get('message')
        self.show_type = kwargs.get('show_type', settings.MESSAGE_SHOW_TYPE['TOAST'])
        self.current_time = round(time.time())
        self.status = kwargs.get("status")
        self.success = kwargs.get("success")

    def send(self):
        status = self.__dict__.pop('status')
        return Response(
            data=self.__dict__,
            status=status
        )


class ErrorResponse(BaseResponse):
    def __init__(self, dev_error=None, errors=None, **kwargs):
        super().__init__(**kwargs)
        self.dev_error = dev_error
        self.errors = errors


class SuccessResponse(BaseResponse):
    def __init__(self, message, data=None, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.data = data
        self.index = kwargs.get('index')
        self.total = kwargs.get('total')


class ExceptionHandlerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    @staticmethod
    def __make_response(status_code: int, extra: dict):
        return {
            'success': True if status_code // 100 == 2 else False,
            'code': status_code,
            'current_time': round(time.time()),
            'show_type': settings.MESSAGE_SHOW_TYPE['NONE'],
            **extra
        }

    @staticmethod
    def process_template_response(request, response):
        if response.status_code == 200 and hasattr(response, 'data') and isinstance(response.data, dict):
            # Ok
            # response.data.update(data)
            response.data = ExceptionHandlerMiddleware.__make_response(200, {
                'index': None,
                'total': None,
                'message': None,
                'data': response.data
            })

        elif response.status_code == 204:
            # No content it will never return data!!! because of 204
            response.data.update(ExceptionHandlerMiddleware.__make_response(204, dict()))

        elif response.status_code == 403:
            # Forbidden

            # IS NOT USED
            # data = {
            #     'errors': response.data,
            #     'dev_error': {
            #         'user': request.user.username, 'api': request.path
            #     }
            # }
            response.data = ExceptionHandlerMiddleware.__make_response(403, {
                'message': 'Permission denied',
                'dev_error': None,
                'errors': None,
                'show_type': settings.MESSAGE_SHOW_TYPE['TOAST']
            })

        elif response.status_code == 401:
            # Unauthorized
            response.data = ExceptionHandlerMiddleware.__make_response(401, {
                'errors': response.data.get('detail', response.data),
                'dev_error':
                    {
                        'user_ip': request.META['REMOTE_ADDR'],
                        'api_address': request.path
                    },
                'message': 'Unauthorized access.',
                'show_type': settings.MESSAGE_SHOW_TYPE['TOAST']
            })

        elif response.status_code == 405:
            # Method Not Allowed
            response.data = ExceptionHandlerMiddleware.__make_response(405, {
                'errors': response.data,
                'dev_error': {
                    'user': request.user.username,
                    'api': request.path
                },
                'message': 'Method not allowed'
            })
        elif response.status_code == 406:
            # 406 Not Acceptable
            response.data = ExceptionHandlerMiddleware.__make_response(406, {
                'errors': response.data,
                'message': _('Not Acceptable request, maybe not supported version'),
                'dev_error': {
                    'user': request.user.username,
                    'api': request.path
                },
            })

        elif response.status_code == 415:
            # 415 Unsupported media type
            response.data = ExceptionHandlerMiddleware.__make_response(415, {
                'errors': response.data,
                'message': _('Unsupported media type'),
                'dev_error': {
                    'user': request.user.username,
                    'api': request.path
                },
            })
        elif response.status_code == 400:
            # Bad Request
            error = response.data.pop('dev_error', None)
            response.data = ExceptionHandlerMiddleware.__make_response(400, {
                'errors': response.data.get('non_field_errors', response.data),
                'dev_error': {
                    'user': request.user.username,
                    'api_address': request.path,
                    'user_ip': request.META['REMOTE_ADDR'],
                    'error': error
                },
                'message': 'Bad request'
            })
        elif response.status_code == 429:
            response.data = ExceptionHandlerMiddleware.__make_response(429, {
                'message': response.data['detail'],
                'dev_error': {
                    'user': request.user.username,
                    'api': request.path
                },
            })
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
