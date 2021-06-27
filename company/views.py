from datetime import datetime, timedelta
import itertools

from querystring_parser import parser
from django.contrib.auth.models import User
from django.core.exceptions import FieldError
from django.core.cache import cache
from django.db.models import Count, Q, F, Case, When, Prefetch, Value, CharField
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import decorators, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle
from packaging import version

from company import serializers as company_serialzier
from review import serializers as review_serialzier
from question import serializers as question_serializer
from company import models
from donate.models import Donate
from donate.serializers import DonateSerializer
from review.models import CompanyReview, Interview
from utilities.tools import create, delete, list_result, update
from utilities.utilities import CUSTOM_PAGINATION_SCHEMA, back_months_by_3, avg_by_key
from utilities import permissions, responses
from utilities.exceptions import CustomException


# Benefit
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class BenefitCreateView(create.CreateView):
    """
    name Required
    """
    serializer_class = company_serialzier.BenefitSerializer
    model = models.Benefit
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class BenefitListView(list_result.ListView):
    serializer_class = company_serialzier.BenefitSerializer
    model = models.Benefit
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserBenefitListView(list_result.UserListView):
    serializer_class = company_serialzier.UserBenefitSerializer
    model = models.Benefit
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class BenefitUpdateView(update.UpdateView):
    serializer_class = company_serialzier.BenefitSerializer
    model = models.Benefit
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class BenefitDeleteView(delete.DeleteView):
    serializer_class = company_serialzier.BenefitSerializer
    model = models.Benefit
    throttle_classes = []


# City
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CityCreateView(create.CreateView):
    """
    name Required

    province object need name of province Required
    """
    serializer_class = company_serialzier.CitySerializer
    model = models.City
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CityListView(list_result.ListView):
    serializer_class = company_serialzier.CitySerializer
    model = models.City
    throttle_classes = []


@decorators.authentication_classes([])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserCityListView(list_result.UserListView):
    """
    get:
        public/city/list/?name=اصفه
    """
    serializer_class = company_serialzier.UserCitySerializer
    model = models.City
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())
            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size = index + size

            result = cache.get(settings.CITY_CACHE_LIST)
            if not result:
                result = self.model.objects.filter(is_deleted=False).order_by('-priority').all()
                result = self.get_serializer(result, many=True).data
                cache.set(settings.CITY_CACHE_LIST, result, timeout=None)

            if arguments.get('name'):
                city_name = arguments.get('name').lower()
                result = list(filter(lambda x: city_name in x['name'].lower(), result))
            total = len(result)
            result = result[index:size]

            return responses.SuccessResponse(result, index=index, total=total).send()
        except FieldError as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CityUpdateView(update.UpdateView):
    serializer_class = company_serialzier.CitySerializer
    model = models.City
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CityDeleteView(delete.DeleteView):
    serializer_class = company_serialzier.CitySerializer
    model = models.City
    throttle_classes = []


# Company
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CompaniesApproveView(generics.CreateAPIView):
    """
     Query param : count, min 1 max 1000
    """
    serializer_class = company_serialzier.ApproveCompaniesSerializer
    throttle_classes = []

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid(raise_exception=True):
                count = serialized_data.data['count']
                
                companies = models.Company.objects.filter(approved=False, user_generated=False)[:count]

                if len(companies) == 0:
                    raise CustomException(detail='Not enough companies to activate')
                else:
                    for company in companies:
                        company.approved = True
                        company.save()
                    return responses.SuccessResponse().send()
        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CompanyCreateView(create.CreateView):
    """
    Industry object need industry name

    Benefit object need benefit name

    Gallery {
        "path": ""  Required
        "description": ""  Can be blank
    }

    Office {

        "name": ""  Used for show name in this format: company name + city name + office name  Max 50, min 3

        "tell": ""  Max 14 , min 10

        "site": ""  Max 100, min 5

        "explanation": ""  Max 3000

        "latitude": ""  23.2356

        "longitude": ""  23.2365

        "working_hours_start": ""  08:00

        "working_hours_stop": ""  17:00

        "size": ""  ["VS", "S", "M", "L", "VL", "UL"] Required

        "city": {} need city id and city name Required

    }
    """
    serializer_class = company_serialzier.CompanySerializer
    model = models.Company
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CompanyInsertView(create.CreateView):
    """

    Gallery {
        "path": ""  Required
        "description": ""  Can be blank
    }

    "name": ""  Used for show name  Max 50, min 3

    "tell": ""  Max 14 , min 10

    "site": ""  Max 100, min 5

    "address": ""  Max 200

    "explanation": ""  Max 3000

    "city": need city name Required

    "logo": Path to media server
    
    """
    serializer_class = company_serialzier.InsertCompanySerializer
    model = models.Company
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class UserCompanyInsertView(create.CreateView):
    """

    Gallery {
        "path": ""  Required
        "description": ""  Can be blank
    }

    "name": ""  Used for show name  Max 50, min 3

    "name_en": ""  Used for show name  Max 50, min 3

    "tell": ""  Max 14 , min 10

    "site": ""  Max 100, min 5

    "address": ""  Max 200

    "explanation": ""  Max 3000

    "city": {"city_slug": ""} need city name Required

    "logo": Path to media server
    
    """
    serializer_class = company_serialzier.UserInsertCompanySerializer
    model = models.Company
    throttle_classes = [UserRateThrottle]


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
class CompanyRetrieveView(generics.RetrieveAPIView):
    """
    get data of a certain company for user
    """
    serializer_class = company_serialzier.UserCompanySerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(approved=True).get(company_slug=slug)
            if not isinstance(request.user, AnonymousUser):  # view of company
                instance.view.add(request.user)
            instance.total_view += 1
            instance.save()
            serialize_data = self.get_serializer(instance)
            return responses.SuccessResponse(serialize_data.data).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyReviewListView(generics.ListAPIView):
    """
    List of reviews of a company

    have pagination

    filter and sort is not developed
    """
    serializer_class = review_serialzier.UserCompanyReviewListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False, approved=True).get(company_slug=slug)
            serialize_data = self.get_serializer(instance.companyreview_set.filter(
                is_deleted=False, approved=True
            ).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AdminCompanyReviewListView(generics.ListAPIView):
    serializer_class = review_serialzier.UserCompanyReviewListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False).get(company_slug=slug)
            if request.user != instance.user:
                return responses.ErrorResponse(message='No permission.', status=403).send()
            serialize_data = self.get_serializer(instance.companyreview_set.filter(is_deleted=False,).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyInterReviewListView(generics.ListAPIView):
    """
    List of interviews of a company

    have pagination

    filter and sort is not developed
    """
    serializer_class = review_serialzier.UserInterviewListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False, approved=True).get(company_slug=slug)
            serialize_data = self.get_serializer(instance.interview_set.filter(
                is_deleted=False, approved=True
            ).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AdminCompanyInterReviewListView(generics.ListAPIView):
    serializer_class = review_serialzier.UserInterviewListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False).get(company_slug=slug)
            if request.user != instance.user:
                return responses.ErrorResponse(message='No permission.', status=403).send()
            serialize_data = self.get_serializer(instance.interview_set.filter(is_deleted=False).all(), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            data = sorted(data, key=lambda x: x['vote_count'], reverse=True)
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyQuestionListView(generics.ListAPIView):
    """
    List of questions of a company

    have pagination

    filter and sort is not developed
    """
    serializer_class = question_serializer.PublicQuestionSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False, approved=True).get(company_slug=slug)
            serialize_data = self.get_serializer(instance.question_set.filter(
                is_deleted=False, approved=True
            ), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class AdminCompanyQuestionListView(generics.ListAPIView):
    serializer_class = question_serializer.PublicQuestionSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            instance = self.model.objects.filter(is_deleted=False).get(company_slug=slug)
            if request.user != instance.user:
                return responses.ErrorResponse(message='No permission.', status=403).send()
            serialize_data = self.get_serializer(instance.question_set.filter(is_deleted=False), many=True)
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            data = serialize_data.data
            return responses.SuccessResponse(data[index:size], index=index, total=len(data)).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyListView(list_result.ListView):
    serializer_class = company_serialzier.CompanySerializer
    model = models.Company
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserCompanyListView(list_result.UserListView):
    """
    Public company list

    /public/company/list/?name=sn&city=Rasht&salary_avg_lte=3.5&salary_avg_gte=1.2&rate_lte=4$rate_gte=2

    salary will * 1,000,000

    order_by HOTTEST, SALARY, RATE
    """
    serializer_class = company_serialzier.PublicCompanyListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())
            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            query_filter = {'approved': True, 'is_deleted': False, 'is_cheater': False}
            if arguments.get('city'):
                query_filter['city__city_slug'] = arguments.get('city')
            if arguments.get('deleted'):
                query_filter['has_legal_issue'] = arguments.get('deleted').capitalize()
            if arguments.get('industry'):
                query_filter['industry__industry_slug'] = arguments.get('industry')
            if arguments.get('salary_avg_lte'):
                query_filter['salary_avg__lte'] = float(arguments.get('salary_avg_lte'))
            if arguments.get('salary_avg_gte'):
                query_filter['salary_avg__gte'] = float(arguments.get('salary_avg_gte'))
            if arguments.get('rate_gte'):
                query_filter['over_all_rate__gte'] = float(arguments.get('rate_gte'))
            if arguments.get('rate_lte'):
                query_filter['over_all_rate__lte'] = float(arguments.get('rate_lte'))
            result = self.model.objects.filter(**query_filter)
            if arguments.get('name'):
                result = result.filter(Q(name__icontains=arguments.get('name')) |
                                       Q(name_en__icontains=arguments.get('name')))
            if arguments.get('order_by'):
                if arguments.get('order_by') == 'HOTTEST':
                    result = result.order_by('-total_review', '-created')
                elif arguments.get('order_by') == 'SALARY':
                    result = result.order_by('-salary_avg', '-created')
                elif arguments.get('order_by') == 'RATE':
                    result = result.order_by('-over_all_rate', '-created')
                else:
                    result = result.order_by('-total_review', '-created')
            else:
                result = result.order_by('-total_review', '-created')
            result = result.prefetch_related(Prefetch('gallery_set',
                                                      queryset=models.Gallery.objects.filter(is_deleted=False),
                                                      to_attr='gallery'))
            result = result.values('name', 'company_slug', 'founded', 'logo', 'city__name', 'city__show_name',
                                   'city__city_slug', 'description', 'total_review', 'total_interview', 'salary_min',
                                   'salary_max', 'over_all_rate', 'size',  'has_legal_issue')
            total = len(result)
            result = self.get_serializer(result[index:size], many=True).data

            return responses.SuccessResponse(result, index=index, total=total).send()
        except FieldError as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class CompanyNameListView(generics.ListAPIView):
    """
    Company names for search in home

    /public/company/name_list/?name__icontains=sn
    """
    serializer_class = company_serialzier.CompanyNameListSerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())

            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            result = cache.get(settings.COMPANY_NAME_LIST)
            if not result:
                result = self.model.objects.filter(is_deleted=False, approved=True)
                result = result.order_by('-total_review')
                result = self.get_serializer(result, many=True).data
                cache.set(settings.COMPANY_NAME_LIST, result, timeout=None)

            if arguments.get('name'):
                name = arguments.get('name').lower()
                result = list(filter(lambda x: name in x['name'].lower() or name in x['name_en'].lower(), result))
            # if arguments.get('name__icontains'):
            #     result = result.filter(Q(name__icontains=arguments.get('name__icontains'))|
            #                            Q(name_en__icontains=arguments.get('name__icontains')))
            # result = result.order_by('-total_review')
            # result = result.all()
            total = len(result)

            return responses.SuccessResponse(result[index:size], index=index, total=total).send()
        except FieldError as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyUpdateView(update.UpdateView):
    """
    for updating office and gallery id is required
    if id didn't send with data new office/gallery will created and add to company office/gallery list

    """
    serializer_class = company_serialzier.CompanySerializer
    model = models.Company
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class CompanyDeleteView(delete.DeleteView):
    serializer_class = company_serialzier.CompanySerializer
    model = models.Company
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CompanyStaticsView(generics.RetrieveAPIView):
    """
    get company statics from panel
    """
    serializer_class = company_serialzier.UserCompanySerializer
    model = models.Company
    throttle_classes = []

    def get(self, request, id, *args, **kwargs):
        try:
            instance = self.model.objects.filter(approved=True).get(id=id)
            if request.user != instance.user:
                return responses.ErrorResponse(message='No permission for statics.', status=403).send()
            data = {
                'total_page_view': instance.total_view,
                'site_users_view': instance.view.count(),
                'total_review': instance.companyreview_set.filter(is_deleted=False, approved=True).count(),
                'total_interview': instance.interview_set.filter(is_deleted=False, approved=True).count(),
                'work_life_balance': instance.work_life_balance,
                'salary_benefit': instance.salary_benefit,
                'security': instance.security,
                'management': instance.management,
                'culture': instance.culture,
                'over_all_rate': instance.over_all_rate,
                'salary_avg': instance.salary_avg,
                'salary_max': instance.salary_max,
                'salary_min': instance.salary_min,
                'recommend_to_friend': instance.recommend_to_friend,
                'company_score': instance.company_score,
            }
            return responses.SuccessResponse(data).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


# Industry
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class IndustryCreateView(create.CreateView):
    serializer_class = company_serialzier.IndustrySerializer
    model = models.Industry
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class IndustryListView(list_result.ListView):
    serializer_class = company_serialzier.IndustrySerializer
    model = models.Industry
    throttle_classes = []


@decorators.authentication_classes([])
@decorators.permission_classes([])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class UserIndustryListView(list_result.UserListView):
    serializer_class = company_serialzier.PublicIndustrySerializer
    # model = models.Industry
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            arguments = parser.parse(request.GET.urlencode())
            size = int(arguments.pop('size', 20))
            index = int(arguments.pop('index', 0))
            size, index = permissions.pagination_permission(request.user, size, index)
            size = index + size
            result = cache.get(settings.INDUSTRY_LIST)
            if not result:
                result = models.Industry.objects.filter(is_deleted=False).values('name', 'industry_slug', 'logo', 'icon')\
                    .distinct().annotate(Count('company', distinct=True)).order_by('-company__count')
                result = self.get_serializer(result, many=True).data
                cache.set(settings.INDUSTRY_LIST, result, timeout=None)
            total = len(result)
            result = result[index:size]
            return responses.SuccessResponse(result, index=index, total=total).send()
        except FieldError as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class IndustryUpdateView(update.UpdateView):
    serializer_class = company_serialzier.IndustrySerializer
    model = models.Industry
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class IndustryDeleteView(delete.DeleteView):
    serializer_class = company_serialzier.IndustrySerializer
    model = models.Industry
    throttle_classes = []


# Province
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProvinceCreateView(create.CreateView):
    """
    name Required
    """
    serializer_class = company_serialzier.ProvinceSerializer
    model = models.Province
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
@decorators.schema(CUSTOM_PAGINATION_SCHEMA)
class ProvinceListView(list_result.ListView):
    serializer_class = company_serialzier.ProvinceSerializer
    model = models.Province
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProvinceUpdateView(update.UpdateView):
    serializer_class = company_serialzier.ProvinceSerializer
    model = models.Province
    throttle_classes = []


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class ProvinceDeleteView(delete.DeleteView):
    serializer_class = company_serialzier.ProvinceSerializer
    model = models.Province
    throttle_classes = []


@decorators.authentication_classes([])
@decorators.permission_classes([])
class HomeView(generics.ListAPIView):
    """
    Home
    """
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            industry_list = cache.get(settings.INDUSTRY_LIST)
            if not industry_list:
                industry_list = company_serialzier.PublicIndustrySerializer(
                    models.Industry.objects.filter(company__approved=True).values('name', 'industry_slug', 'icon', 'logo')
                        .distinct().annotate(Count('company', distinct=True)).order_by('-company__count'),
                    many=True).data
                cache.set(settings.INDUSTRY_LIST, industry_list, timeout=None)

            company_list = cache.get(settings.BEST_COMPANY_LIST)
            if not company_list:
                company_list = company_serialzier.PublicCompanyListSerializer(
                    models.Company.objects.filter(is_deleted=False, approved=True, is_cheater=False).order_by('-company_score').
                        values('name', 'company_slug', 'founded', 'logo', 'city__name', 'city__show_name',
                               'city__city_slug', 'description', 'total_review', 'total_interview', 'salary_min',
                               'salary_max', 'over_all_rate', 'size',  'has_legal_issue', 'company_score').distinct()[:10],
                    many=True).data
                cache.set(settings.BEST_COMPANY_LIST, company_list, timeout=None)

            discussed_company_list = cache.get(settings.DISCUSSED_COMPANY_LIST)
            if not discussed_company_list:
                discussed_company_list = company_serialzier.PublicCompanyListSerializer(
                    models.Company.objects.filter(is_deleted=False, approved=True, is_cheater=False).
                        annotate(total_sum=F('total_review') + F('total_interview')).
                        order_by('-total_sum').values('name', 'company_slug', 'founded', 'logo', 'city__name',
                                                      'city__show_name', 'city__city_slug', 'description',
                                                      'total_review', 'total_interview', 'salary_min', 'salary_max',
                                                      'over_all_rate', 'size',  'has_legal_issue').distinct()[:10],
                    many=True).data
                cache.set(settings.DISCUSSED_COMPANY_LIST, discussed_company_list, timeout=None)

            context = {'request': request}
            if version.parse(request.version) < version.parse('1.0.1'):
                last_reviews = cache.get(settings.LAST_REVIEWS)
                if not last_reviews:
                    last_reviews = review_serialzier.UserHomeCompanyReviewListSerializer(
                        CompanyReview.objects.filter(approved=True, is_deleted=False).order_by('-created')
                            .values('id', 'company__name', 'company__name_en', 'company__company_slug', 'company__logo',
                                    'title', 'description', 'over_all_rate', 'created', 'has_legal_issue',
                                    'approved', 'creator').distinct()[:10],
                        many=True, context=context).data
                    cache.set(settings.LAST_REVIEWS, last_reviews, timeout=None)

                last_interviews = cache.get(settings.LAST_INTERVIEWS)
                if not last_interviews:
                    last_interviews = review_serialzier.UserHomeInterviewListSerializer(
                        Interview.objects.filter(approved=True, is_deleted=False).order_by('-created')
                        .values('id', 'company__name', 'company__name_en', 'company__company_slug', 'company__logo',
                                'title', 'description', 'created', 'total_rate', 'approved', 'has_legal_issue', 'creator',
                                ).distinct()[:10],
                        many=True, context=context).data
                    cache.set(settings.LAST_INTERVIEWS, last_interviews, timeout=None)
            else:
                arguments = parser.parse(request.GET.urlencode())
                size = int(arguments.pop('size', 20))
                index = int(arguments.pop('index', 0))
                size, index = permissions.pagination_permission(request.user, size, index)
                size = index + size
                lcr = CompanyReview.objects.filter(approved=True,
                                                   is_deleted=False).annotate(
                    type=Value('REVIEW', output_field=CharField())) \
                    .values('id', 'company__name', 'company__name_en',
                            'company__company_slug', 'company__logo',
                            'title', 'description', 'over_all_rate', 'created',
                            'has_legal_issue',
                            'approved', 'creator', 'type').distinct()
                lir = Interview.objects.filter(approved=True, is_deleted=False).annotate(
                    type=Value('INTERVIEW', output_field=CharField())) \
                    .values('id', 'company__name', 'company__name_en',
                            'company__company_slug', 'company__logo',
                            'title', 'description', 'total_rate', 'created',
                            'has_legal_issue',
                            'approved', 'creator', 'type').distinct()

                lqq = lcr.union(lir, all=True)
                lqq = lqq.order_by('-created')
                total = lqq.count()
                reviews = review_serialzier.UserHomeReviewListSerializer(
                    lqq[index:size], many=True, context=context
                ).data

            donate = cache.get(settings.DONATE_LIST, None)
            if donate is None:
                donate = {'THE_MOST': DonateSerializer(Donate.objects.filter(is_active=True).exclude(cost__lte=0).order_by('-cost')[:24],
                                                       many=True).data,
                          'THE_LAST': DonateSerializer(Donate.objects.filter(is_active=True).exclude(cost__lte=0).order_by('-created')[:24],
                                                       many=True).data}
                cache.set(settings.DONATE_LIST, donate)

            quote_list = [
                {
                    'name': 'جادی',
                    'skill': 'برنامه نویس خوشحال',
                    'description': 'یکی از چیزهایی که توی ایران جاش خالی بوده، بررسی جاهایی بوده که توشون کار کردیم.'
                                   ' ستاره دادن و نظر نوشتن و .. تیم جاب گای داره اینکار رو می کنه.'
                                   ' خوبه چک کنین یا اگر تجربه ای دارین توش بنویسین که کیفیت زندگی خودمون رو بالاتر ببریم'
                                   '    https://jadi.net/2019/08/doshanbe-9805/    '
                },
                {
                    'name': 'Ashkan',
                    'skill': 'Software Developer',
                    'description': 'من بعضا می‌بینم می‌گن جابگای خوب نیست چون نظرات بررسی، تحقیق و درستی سنجی نمیشه!!!! '
                                   'پیشنهادم نه تنها در مورد جابگای بلکه همه چیزهای دیگه که در '
                                   'اینترنت می‌خونید اینه که خودتون در موردش تحقیق و درستی سنجی کنید'
                                   ' جابگای و پلتفرمای دیگه فضایی رو ایجاد می‌کنن تا بشه نظرات رو یکجا خوند.',
                },
                {
                    'name': 'شهاب',
                    'skill': 'Developer',
                    'description': 'مدتی بود به این فکر می کردم که اکوسیستم استارتاپی در ایران، به چنین پلتفرمی نیاز داره. '
                                   'هزاران شرکت در ایران وجود داره که اطلاع دقیقی از درون آنها موجود نیست. '
                                   'هر فردی برای پیوستن به شرکت یا تیم جدید به اطلاعات مختلفی برای تصمیم گیری نیاز داره.'
                                   ' چگونگی رفتار با کارمندان، میزان حقوق، دیر کرد در پرداخت حقوق و ...'
                                   ' سوالاتیست که برای همه افراد به هنگام پیوستن به شرکت جدید ایجاد میشه.'
                                   ' چنین اطلاعاتی از شرکت های ایرانی موجود نیست.'
                                   ' شفافیت در این زمینه ها منجر به ایجاد رقابت بین شرکت ها و رشد اکوسیستم میشه.',
                },
                {
                    'name': 'Ali',
                    'skill': 'مهندس نرم افزار',
                    'description': 'با توجه به اتفاقاتی که برای jobguy‌.‌ir تجربه کاری برای همه افتاده، '
                                   'به نظرم خیلی مهم هست که از اینجا به بعد ،همه ما تجربه های کاری ای که داشتیم '
                                   '(چه مثبت چه منفی،فارغ از هرگونه نگاه جانب دارانه ) رو "بیشتر از قبل" منتشر کنیم ،'
                                   'اهمیت و چرایی این قضیه کاملا روشنه و فکر نمیکنم نیازی به توضیح اضافی باشه.',
                },
                {
                    'name': 'Hasan',
                    'skill': '',
                    'description': 'جالبه یه سری شرکت‌ها که اسم‌شون جزو ۵۰ شرکت «برتر» ایران برای کار جابینجاست،'
                                   ' از @JobguyIR درخواست حذف اطلاعات کردن ',
                },
                {
                    'name': 'آیین',
                    'skill': 'مهندس نرم افزار',
                    'description': 'خیلی وقت بود که نیاز به چیزی مثل @JobguyIR نیاز بود! همچین ابزاری باید جدی گرفته بشه،'
                                   ' شرکت‌ها باید ببینن که کارمنداشون چی فکر میکنن درموردشون و کارمندها'
                                   ' هم باید یه فضای امن برای راحت نظر دادن داشته باشن. این چیزیه که جاب‌گای ارائه میده.',
                },
                {
                    'name': 'Ashkan',
                    'skill': 'Software Developer',
                    'description': 'یه چیزی بگم در مورد جابگای:- نظرات مثبت رو باور نکنید (اگه تعریفی باشه، کارمندا تو'
                                   ' شبکه‌های اجتماعی مثل توییتر با اسم و مشخصات تعریف می‌کنن)'
                                   '- نظرات منفی رو هم (تا حدی) معیار رد کردن نذارید و باهاش اولویت بندی کنید'
                                   '* اما، اگر نظرات تو جابگای حذف شده بود، بیخیال اون شرکت بشید.',
                },
                {
                    'name': 'Todd',
                    'skill': 'Developer',
                    'description': 'همین  @JobguyIR دارید تعطیلش می‌کنید '
                                   'به من کمک کرد تا تو یه شرکت بد استخدام نشم. دقیقا روزی که قرار بود قرارداد'
                                   ' امضا کنم و مشغول کار بشم، گفتم بزار یه سرچ بزنم و تمامی نظرات منفی بود. از موبایل '
                                   'دولوپرشون بگیر تا وب و بک‌اند و ... باعث شد درآمدم زیاد نشه اما راضیم از اینکه نرفتم'
                },
            ]

            jobguy_text = [
                'تجربه کاری برای همه',
                'تجربه کاری و تجربه مصاحبه دیگران رو بخون',
                'مسیر شغلیت رو بهتر انتخاب کن',
                'تجربه کاری خودت رو با دیگران به اشتراک بگذار',
                'به بهبود شرایط کاری در شرکت های ایرانی کمک کن'
            ]

            total_review = cache.get(settings.TOTAL_REVIEW)
            if not total_review:
                total_review = CompanyReview.objects.filter(company__approved=True, company__is_deleted=False,
                                                            is_deleted=False, approved=True).count()
                cache.set(settings.TOTAL_REVIEW, total_review, timeout=None)

            total_interview = cache.get(settings.TOTAL_INTERVIEW)
            if not total_interview:
                total_interview = Interview.objects.filter(company__approved=True, company__is_deleted=False,
                                                           is_deleted=False, approved=True).count()
                cache.set(settings.TOTAL_INTERVIEW, total_interview, timeout=None)

            total_user = cache.get(settings.TOTAL_USER)
            if not total_user:
                total_user = User.objects.count()
                cache.set(settings.TOTAL_USER, total_user, timeout=None)

            total_company = cache.get(settings.TOTAL_COMPANY)
            if not total_company:
                total_company = models.Company.objects.filter(is_deleted=False, approved=True).count()
                cache.set(settings.TOTAL_COMPANY, total_company, timeout=None)

            temp_data = {
                'industries': industry_list[:8],
                'company': company_list,
                'discussed_company_list': discussed_company_list,
                'jobguy_text': jobguy_text,
                'quote': quote_list,
                'total_review': total_review,
                'total_interview': total_interview,
                'total_user': total_user,
                'total_company': total_company,
                'donate': donate,
            }
            if version.parse(request.version) < version.parse('1.0.1'):
                temp_data.update({
                    'last_reviews': last_reviews,
                    'last_interviews': last_interviews,
                })
                return responses.SuccessResponse(temp_data).send()
            else:
                temp_data.update({
                    'reviews': reviews,
                })
                return responses.SuccessResponse(temp_data, index=index, total=total).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([])
@decorators.permission_classes([])
class HomeFAQView(generics.ListAPIView):
    """
    Home FAQ
    """
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        try:
            data = [
                {
                    "question": "هدف پلتفرم جابگای چیست؟",
                    "answer": "به اشتراک گذاری تجربه‌ کاری و تجربه مصاحبه در شرکت ها"
                              " به منظور شناخت بهتر و بهبود شرایط کاری."
                },
                {
                    "question": "اطلاعات کاربران تا چه حد محرمانه است؟",
                    "answer": "اطلاعاتی کاربران برای جابگای بسیار مهم است "
                              "و تمام تلاش به منظور حفظ این اطلاعات از دست افراد غیر انجام می شود."
                },
                {
                    "question": "چه تجربه ای رو ثبت کنم؟",
                    "answer": "ثبت هر نوع تجربه که قوانین پلتفرم جابگای(بدون افشای اطلاعات محرمانه شرکت،"
                              " توهین به شرکت یا اشخاص و...) را نقض نکرده باشد، امکان پذیر است."
                              " تنها درخواست ما از کاربران، ثبت تجربه های واقعی و بدون تعصب است."
                },
                {
                    "question": "با چه مجوز حقوقی برای شرکت پروفایل ایجاد می‌کنید؟",
                    "answer": "اطلاعات منتشر شده در پروفایل هر شرکت توسط هیچ قانونی به صراحت و یا ضمنی ممنوع نشده است."
                              " در بسیاری از کشورهای دنیا این داده‌ها به عنوان داده‌ی باز مطرح شده "
                              "و مجوزهای قانونی مرتبط برای آن توسعه یافته است."
                },
                {
                    "question": "آیا شرکت می تواند به تجربه های ثبت شده پاسخ دهد؟",
                    "answer": "شرکت در صورت نیاز می تواند پاسخ خود نسبت به تجربه ثبت شده را در پایین تجربه ثبت کند."
                },
                {
                    "question": "آیا شرکت می تواند پنل اختصاصی برای ویرایش اطلاعات داشته باشد؟",
                    "answer": "به منظور دریافت پنل اختصاصی کافی است با استفاده از ایمیل رسمی شرکت با ما در تماس باشید."
                },
                {
                    "question": "چطور شرکت جدید رو به پلتفرم اضافه کنم؟",
                    "answer": "اطلاعات شرکت یا نام و آدرس اینترنتی شرکت رو برای ما ارسال کنید."
                },
                {
                    "question": "چقدر میشه به تجربه‌های ثبت شده بر روی شرکت ها اطمینان کرد؟",
                    "answer": "جابگای هیچ مسئولیتی در رابطه با تجربه شخصی افراد ندارد، "
                              "تجربه هر شخص فارغ از واقعی یا ساختگی بودن، "
                              "نظر شخصی فرد است و صحیح یا غلط بودن آن برای پلتفرم قابل تشخیص نیست. "
                              "نتیجه گیری در رابطه با تجربه های دیگران بر عهده خوانند تجربیات است."
                },
                {
                    "question": "مخاطب تجربه‌های ثبت شده کیست؟",
                    "answer": "در وهله اول مخاطب تجربه های ثبت شده مدیران شرکت و منابع انسانی هستند "
                              "تا با نظرات و تجربه های واقعی کارمندان آشنا شوند "
                              "و در پی بهبود شرایط کاری در شرکت خود باشند. "
                              "همچنین افرادی که قصد شروع همکاری با شرکت ها رو دارند می توانند"
                              " از تجربه های ثبت شده کارکنان قبلی شرکت به منظور شناخت بهتر استفاده کنند. "
                },
                {
                    "question": "تعداد بازدید ها چگونه حساب می شود؟",
                    "answer": "بازدید در سایت به دو صورت محاسبه می شود."
                              " بازدیدی که در پایین تجربه ها اعلام می شود تعداد درخواست زده شده به سمت سرور است."
                              " نوع دیگر تعداد بازدید ها که به صورت یکتا ثبت می شود"
                              " نیز بر روی تجربه های پنل مدیریت شرکت موجود است."
                },
                {
                    "question": "شیوه رتبه بندی شرکت های برتر چگونه است؟",
                    "answer": "فاکتور های مختلفی در امتیاز دهی شرکت ها و در نهایت رتبه بندی آنها وجود دارد."
                              " تعداد تجربه های ثبت شده."
                              " امتیاز داده شده به شرکت در تجربه های ثبت شده و ..."
                },
            ]
            return responses.SuccessResponse(data).send()
        except Exception as e:
            return responses.ErrorResponse(message=str(e)).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([])
class CompanySalaryChartView(generics.ListAPIView):
    """
    Company Salary Chart
    """
    throttle_classes = []

    def get(self, request, slug, *args, **kwargs):
        try:
            company = models.Company.objects.filter(is_deleted=False, approved=True).get(company_slug=slug)
            data = []
            undone_months = list(range(8, 0, -1))
            end_time = datetime.now()
            start_time = end_time - timedelta(days=8 * 90)
            if not company.has_legal_issue:
                reviews = company.companyreview_set.filter(created__range=(start_time, end_time)).\
                    annotate(publish_time=Case(When(end_date__isnull=True, then=F('created')), default=F('end_date'))).\
                    order_by('publish_time').values('salary', 'publish_time')
                groups = itertools.groupby(reviews, lambda x: back_months_by_3(x['publish_time'], end_time))

                for group, match in groups:
                    if group:
                        undone_months.remove(group)
                        reviews_count, reviews_avg_salary = avg_by_key(list(match), 'salary')
                        data.append({
                            'id': group,
                            'time': (end_time - timedelta(days=group*90) + timedelta(days=45)).strftime('%Y-%m-%d'),
                            'salary': reviews_avg_salary,
                            'reviews': reviews_count,
                        })
            for i in undone_months:
                data.append({
                    'id': i,
                    'time': (end_time - timedelta(days=i * 90) + timedelta(days=45)).strftime('%Y-%m-%d'),
                    'salary': 0,
                    'reviews': 0,
                })
            return responses.SuccessResponse(sorted(data, key=lambda x:x['id'])).send()
        except models.Company.DoesNotExist as e:
            return responses.ErrorResponse(message='Instance does not Found.', status=404).send()

        except ValidationError as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
