import requests
import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from django.db import transaction
from rest_framework import generics
from rest_framework import decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.parsers import MultiPartParser
import pandas as pd

from utilities import responses
from config.models import IntegerConfig
from company.models import Company
from utilities.permissions import SuperUserPermission
from utilities.utilities import CUSTOM_UPLOAD_SCHEMA, file_check_name
from utilities.serializers import FileUploadSerializer, MergeCompanySerializer


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated,SuperUserPermission])
@decorators.schema(CUSTOM_UPLOAD_SCHEMA)
class MergeCompanyView(generics.CreateAPIView):
    """
    Merge company data

    merge src data to des and then delete src company

    set id as src and des
    """
    serializer_class = MergeCompanySerializer
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        serialize_data = self.get_serializer(data=request.data)
        if serialize_data.is_valid():
            try:
                src = Company.objects.get(id=serialize_data.validated_data["src"],
                                          is_deleted=False)
            except Company.DoesNotExist as e:
                return responses.ErrorResponse(message="Src company does not exist",
                                               status=400).send()

            try:
                des = Company.objects.get(id=serialize_data.validated_data["des"],
                                          is_deleted=False)
            except Company.DoesNotExist as e:
                return responses.ErrorResponse(message="Des company does not exist",
                                               status=400).send()
            with transaction.atomic():
                # review
                for review in src.companyreview_set.all():
                    review.company = des
                    review.save()

                # interview
                for interview in src.interview_set.all():
                    interview.company = des
                    interview.save()

                # question
                for question in src.question_set.all():
                    question.company = des
                    question.save()

                src.is_deleted = True
                src.save()
            return responses.SuccessResponse({}, status=200).send()
        return responses.ErrorResponse(message="not valid data",
                                       status=400).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_UPLOAD_SCHEMA)
class FileUploadView(generics.CreateAPIView):
    """
    File uploader

    File max size is 50 MB
    """
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        serialize_data = self.get_serializer(data=request.data)
        if serialize_data.is_valid():
            file = file_check_name(request.user.username, serialize_data.validated_data['file'],
                                   serialize_data.validated_data['slug'])
            data = {'file_path': file}
            return responses.SuccessResponse(data, status=200).send()
        else:
            dev_error = serialize_data.errors
            message = 'Failed to upload {}'.format(serialize_data.data['file'].name)
            show_type = settings.MESSAGE_SHOW_TYPE['TOAST']
            return responses.ErrorResponse(message=message, dev_error=dev_error, show_type=show_type,
                                           status=400).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class CreateDataTestView(generics.RetrieveAPIView):
    """
    Data test
    """
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            main_url = '{}/'.format(request.build_absolute_uri('/')[:-1].strip("/"))
            create_data(main_url)  # for debug
            data = {}
            return responses.SuccessResponse(data).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e), status=400).send()


def create_data(main_url):

    print('Cleaning previous database')
    call_command('migrate')
    print('Set initial configs')
    IntegerConfig(name='SUGGESTION_TIMEOUT', value=60 * 5, description='Redis timeout for suggestion').save()
    IntegerConfig(name='MAX_SMS_PER_TIME_OUT', value=3, description='Max send sms in a timeout').save()
    IntegerConfig(name='SMS_TIMEOUT', value=30 * 60, description='Sms timeout ').save()
    IntegerConfig(name='MAX_FILE_SIZE', value=2*1024*1024, description='Max file size to upload').save()
    IntegerConfig(name='VERIFICATION_TIME_OUT', value=10 * 60, description='Timeout to verify mobile').save()

    url_map = {
        'MAIN_URL': main_url,
        'REGISTER_EMAIL': 'authnz/register_email/',
        'LOGIN_EMAIL': 'authnz/login_email/',
        'BENEFIT_CREATE': 'benefit/create/',
        'INDUSTRY_CREATE': 'industry/create/',
        'PROVINCE_CREATE': 'province/create/',
        'CITY_CREATE': 'city/create/',
        'COMPANY_CREATE': 'company/create/',
        'JOB_CREATE': 'job/create/',
        'PROS_CREATE': 'pros/create/',
        'CONS_CREATE': 'cons/create/',
        'COMPANY_REVIEW_CREATE': 'company_review/create/',
        'QUESTION_CREATE': 'question/create/',
        'ANSWER_CREATE': 'answer/create/',
    }

    ADMIN_DATA = {'email': 'admin@jobguy.work', 'password': '2e8d9375bbdb401e46d2251c7175'}
    resp = requests.post(url_map['MAIN_URL'] + url_map['REGISTER_EMAIL'], json=ADMIN_DATA)
    resp = requests.post(url_map['MAIN_URL'] + url_map['LOGIN_EMAIL'], json=ADMIN_DATA)
    user = User.objects.last()
    user.is_staff = True
    user.is_superuser = True
    user.save()
    ADMIN_HEADER = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + resp.json()['data']['token']
    }
    excel_file = 'data_test.xlsx'
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, excel_file)
    xl = pd.ExcelFile(file_path)
    df = xl.parse('provinces')
    PROVINCE_DATA = {}
    for index, row in df.iterrows():
        # Province
        PROVINCE_DATA_TEMP = {'name': row['name']}
        resp = requests.post(url_map['MAIN_URL'] + url_map['PROVINCE_CREATE'], json=PROVINCE_DATA_TEMP,
                             headers=ADMIN_HEADER)
        PROVINCE_DATA[row['province_id']] = resp.json()['data']

    # City
    df = xl.parse('cities')
    CITY_DATA = {}
    for index, row in df.iterrows():
        CITY_DATA_TEMP = {'name': row['name'], 'province': PROVINCE_DATA[row['province_id']]}
        resp = requests.post(url_map['MAIN_URL'] + url_map['CITY_CREATE'], json=CITY_DATA_TEMP, headers=ADMIN_HEADER)
        CITY_DATA[row['city_id']] = resp.json()['data']

    # Job
    df = xl.parse('job')
    JOB_DATA = {}
    for index, row in df.iterrows():
        JOB_DATA_TEMP = {'name': row['name'], 'description': row['description'], 'cover': row['cover'],
                         'icon': row['icon']}
        resp = requests.post(url_map['MAIN_URL'] + url_map['JOB_CREATE'], json=JOB_DATA_TEMP, headers=ADMIN_HEADER)
        # JOB_DATA[row['job_id']] = resp.json()['data']

    # Industry
    df = xl.parse('industries')
    INDUSTRY_DATA = {}
    for index, row in df.iterrows():
        INDUSTRY_DATA_TEMP = {'name': row['name'], 'logo': row['logo'], 'icon': row['icon'],
                              'description': row['description']}
        resp = requests.post(url_map['MAIN_URL'] + url_map['INDUSTRY_CREATE'], json=INDUSTRY_DATA_TEMP,
                             headers=ADMIN_HEADER)
        INDUSTRY_DATA[row['industry_id']] = resp.json()['data']

    # Pros
    df = xl.parse('pros')
    PROS_DATA = {}
    for index, row in df.iterrows():
        PROS_DATA_TEMP = {'name': row['name'], 'icon': row['icon'], 'logo': row['logo']}
        resp = requests.post(url_map['MAIN_URL'] + url_map['PROS_CREATE'], json=PROS_DATA_TEMP, headers=ADMIN_HEADER)
        # PROS_DATA[row['pros_id']] = resp.json()['data']

    # Cons
    df = xl.parse('cons')
    CONS_DATA = {}
    for index, row in df.iterrows():
        CONS_DATA_TEMP = {'name': row['name'], 'icon': row['icon'], 'logo': row['logo']}
        resp = requests.post(url_map['MAIN_URL'] + url_map['CONS_CREATE'], json=CONS_DATA_TEMP, headers=ADMIN_HEADER)
        # CONS_DATA[row['cons_id']] = resp.json()['data']

    # Company
    df = xl.parse('companies')
    COMPANY_DATA = {}
    for index, row in df.iterrows():
        gallery_list = []
        if isinstance(row['gallery'], str):
            for gallery_path in row['gallery'].split(',')[:-1]:
                gallery_list.append({
                    'path': gallery_path,
                })
        COMPANY_DATA_TEMP = {'name': row['name'], 'name_en': row['name_en'], 'company_slug': row['slug'],
                             'founded': '{}-01-01'.format(row['founded']), 'industry': INDUSTRY_DATA[row['industry']],
                             'size': row['size'], 'city': CITY_DATA[row['city_id']],
                             'cover': row['header'], 'logo': row['logo'],
                             'site': row['website'] if isinstance(row['website'], str) else '',
                             'description': row['description'] if isinstance(row['description'], str) else '',
                             'gallery': gallery_list}
        if not isinstance(row['website'], str):
            COMPANY_DATA_TEMP.pop('site')
        if not isinstance(row['description'], str):
            COMPANY_DATA_TEMP.pop('description')
        if not isinstance(row['founded'], str):
            COMPANY_DATA_TEMP.pop('founded')
        resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_CREATE'], json=COMPANY_DATA_TEMP,
                             headers=ADMIN_HEADER)
        try:
            COMPANY_DATA[row['company_id']] = resp.json()['data']
        except Exception as e:
            print(e)

    # user_data_map = dict()
    # for index, row in df.iterrows():
    # # Benefit
    # BENEFIT_DATA = {'name': 'Test Benefit', 'logo': UPLOAD_IMAGE_PATH, 'icon': ICON}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['BENEFIT_CREATE'], json=BENEFIT_DATA, headers=ADMIN_HEADER)
    # BENEFIT_DATA = resp.json()['data']
    #
    # # Industry
    # INDUSTRY_DATA = {'name': 'Test Industry', 'logo': UPLOAD_IMAGE_PATH, 'icon': ICON,
    #                  'description': 'Test industry description'}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['INDUSTRY_CREATE'], json=INDUSTRY_DATA, headers=ADMIN_HEADER)
    # INDUSTRY_DATA = resp.json()['data']
    #
    # # Company
    # COMPANY_DATA1 = {'name': 'Snapp', 'logo': UPLOAD_IMAGE_PATH, 'industry': INDUSTRY_DATA, 'founded': '2012-02-01',
    #                 'benefit': [BENEFIT_DATA], 'gallery': [{'path': UPLOAD_IMAGE_PATH, 'description': 'Snapp gallery'}],
    #                 'description': 'Online taxi company in iran', 'size': 'L', 'tell': '02123564879',
    #                 'site': 'http://google.com', 'explanation': 'An Internet taxi app for iranian',
    #                 'latitude': 65.254, 'longitude': 64.25, 'working_hours_start': '07:00:00',
    #                 'working_hours_stop': '19:00:00', 'city': CITY_DATA, 'cover': UPLOAD_IMAGE_COVER_PATH,
    #             }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_CREATE'], json=COMPANY_DATA1, headers=ADMIN_HEADER)
    # COMPANY_DATA1 = resp.json()['data']
    #
    # COMPANY_DATA2 = {'name': 'Tap30', 'logo': UPLOAD_IMAGE_PATH, 'industry': INDUSTRY_DATA, 'founded': '2012-02-01',
    #                 'benefit': [BENEFIT_DATA], 'gallery': [{'path': UPLOAD_IMAGE_PATH, 'description': 'Snapp gallery'}],
    #                 'description': 'Online taxi company in iran', 'size': 'L', 'tell': '02123564879',
    #                 'site': 'http://google.com', 'explanation': 'An Internet taxi app for iranian',
    #                 'latitude': 65.254, 'longitude': 64.25, 'working_hours_start': '07:00:00',
    #                 'working_hours_stop': '19:00:00', 'city': CITY_DATA, 'cover': UPLOAD_IMAGE_COVER_PATH,
    #             }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_CREATE'], json=COMPANY_DATA2, headers=ADMIN_HEADER)
    # COMPANY_DATA2 = resp.json()['data']
    #
    # COMPANY_DATA3 = {'name': 'Jobguy', 'logo': UPLOAD_IMAGE_PATH, 'industry': INDUSTRY_DATA, 'founded': '2012-02-01',
    #                 'benefit': [BENEFIT_DATA], 'gallery': [{'path': UPLOAD_IMAGE_PATH, 'description': 'Snapp gallery'}],
    #                 'description': 'Online taxi company in iran', 'size': 'L', 'tell': '02123564879',
    #                 'site': 'http://google.com', 'explanation': 'An Internet taxi app for iranian',
    #                 'latitude': 65.254, 'longitude': 64.25, 'working_hours_start': '07:00:00',
    #                 'working_hours_stop': '19:00:00', 'city': CITY_DATA, 'cover': UPLOAD_IMAGE_COVER_PATH,
    #             }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_CREATE'], json=COMPANY_DATA3, headers=ADMIN_HEADER)
    # COMPANY_DATA3 = resp.json()['data']
    # # Job
    # JOB_DATA = {'name': 'Developer Python', 'description': 'This is a good job :).', 'cover': UPLOAD_IMAGE_PATH, 'icon': ICON}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['JOB_CREATE'], json=JOB_DATA, headers=ADMIN_HEADER)
    # JOB_DATA = resp.json()['data']
    #
    # JOB_DATA = {'name': 'Developer Java Script', 'description': 'This is a good job :).', 'cover': UPLOAD_IMAGE_PATH, 'icon': ICON}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['JOB_CREATE'], json=JOB_DATA, headers=ADMIN_HEADER)
    # JOB_DATA = resp.json()['data']
    #
    # JOB_DATA = {'name': 'Developer IOS', 'description': 'This is a good job :).', 'cover': UPLOAD_IMAGE_PATH, 'icon': ICON}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['JOB_CREATE'], json=JOB_DATA, headers=ADMIN_HEADER)
    # JOB_DATA = resp.json()['data']
    #
    # JOB_DATA = {'name': 'Developer Android', 'description': 'This is a good job :).', 'cover': UPLOAD_IMAGE_PATH, 'icon': ICON}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['JOB_CREATE'], json=JOB_DATA, headers=ADMIN_HEADER)
    # JOB_DATA = resp.json()['data']
    #
    # # Pros
    # PROS_DATA = {'name': 'Pros 1', 'icon': ICON, 'logo': UPLOAD_IMAGE_PATH}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['PROS_CREATE'], json=PROS_DATA, headers=ADMIN_HEADER)
    # PROS_DATA = resp.json()['data']
    #
    # # Cons
    # CONS_DATA = {'name': 'Cons 1', 'icon': ICON, 'logo': UPLOAD_IMAGE_PATH}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['CONS_CREATE'], json=CONS_DATA, headers=ADMIN_HEADER)
    # CONS_DATA = resp.json()['data']
    #
    # # Company Review
    # COMPANY_REVIEW_DATA = {'company': COMPANY_DATA1, 'job': JOB_DATA,
    #                        'recommend_to_friend': True,
    #                        'pros': [
    #                            PROS_DATA
    #                        ],
    #                        'cons': [
    #                            CONS_DATA
    #                        ],
    #                        'state': 'FULL', 'work_life_balance': 3, 'salary_benefit': 4, 'security': 2,
    #                        'management': 3, 'culture': 5, 'title': 'Good second home', 'salary_type': 'MONTH',
    #                        'description': 'This company is very good company', 'salary': 3500000,
    #                        }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_REVIEW_CREATE'],
    #                      json=COMPANY_REVIEW_DATA, headers=ADMIN_HEADER)
    # COMPANY_REVIEW_DATA = resp.json()['data']
    #
    # # Company Review
    # COMPANY_REVIEW_DATA = {'company': COMPANY_DATA1, 'job': JOB_DATA,
    #                        'recommend_to_friend': True,
    #                        'pros': [
    #                            PROS_DATA
    #                        ],
    #                        'cons': [
    #                            CONS_DATA
    #                        ],
    #                        'state': 'FULL', 'work_life_balance': 3, 'salary_benefit': 4, 'security': 2,
    #                        'management': 3, 'culture': 5, 'title': 'Good second home', 'salary_type': 'MONTH',
    #                        'description': 'This company is very good company', 'salary': 3500000,
    #                        }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_REVIEW_CREATE'],
    #                      json=COMPANY_REVIEW_DATA, headers=ADMIN_HEADER)
    # COMPANY_REVIEW_DATA = resp.json()['data']
    #
    # # Company Review
    # COMPANY_REVIEW_DATA = {'company': COMPANY_DATA1, 'job': JOB_DATA,
    #                        'recommend_to_friend': True,
    #                        'pros': [
    #                            PROS_DATA
    #                        ],
    #                        'cons': [
    #                            CONS_DATA
    #                        ],
    #                        'state': 'FULL', 'work_life_balance': 3, 'salary_benefit': 4, 'security': 2,
    #                        'management': 3, 'culture': 5, 'title': 'Good second home', 'salary_type': 'MONTH',
    #                        'description': 'This company is very good company', 'salary': 3500000,
    #                        }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_REVIEW_CREATE'],
    #                      json=COMPANY_REVIEW_DATA, headers=ADMIN_HEADER)
    # COMPANY_REVIEW_DATA = resp.json()['data']
    # COMPANY_REVIEW_DATA = {'company': COMPANY_DATA3, 'job': JOB_DATA,
    #                        'recommend_to_friend': True,
    #                        'pros': [
    #                            PROS_DATA
    #                        ],
    #                        'cons': [
    #                            CONS_DATA
    #                        ], 'anonymous_job': True,
    #                        'state': 'FULL', 'work_life_balance': 5, 'salary_benefit': 4, 'security': 5,
    #                        'management': 5, 'culture': 5, 'title': 'Good second home', 'salary_type': 'MONTH',
    #                        'description': 'This company is very good company', 'salary': 3500000,
    #                        }
    # resp = requests.post(url_map['MAIN_URL'] + url_map['COMPANY_REVIEW_CREATE'],
    #                      json=COMPANY_REVIEW_DATA, headers=ADMIN_HEADER)
    # COMPANY_REVIEW_DATA = resp.json()['data']
    #
    # # Question
    # QUESTION_DATA = {'title': 'What about a question?', 'body': 'Do you know anything about this company?',
    #                  'company': COMPANY_DATA2}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['QUESTION_CREATE'],
    #                      json=QUESTION_DATA, headers=ADMIN_HEADER)
    # QUESTION_DATA = resp.json()['data']
    #
    # # Answer
    # ANSWER_DATA = {'body': 'Yes I know everything about it.', 'question': QUESTION_DATA}
    # resp = requests.post(url_map['MAIN_URL'] + url_map['ANSWER_CREATE'],
    #                      json=ANSWER_DATA, headers=ADMIN_HEADER)
    # ANSWER_DATA = resp.json()['data']

    return responses.SuccessResponse({}).send()
