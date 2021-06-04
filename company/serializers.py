import json
import re
from datetime import datetime, timedelta

from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext

from company.models import Benefit, Company, Industry, Province, City, Gallery
from review.models import Cons, Pros
from utilities import utilities
from utilities.exceptions import CustomException


class IndustrySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=3)
    industry_slug = serializers.ReadOnlyField()
    logo = serializers.CharField(max_length=200, required=False)
    icon = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=2000, required=False)
    supported = serializers.BooleanField(default=True)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['industry_slug'] = utilities.slug_helper(validated_data['name'])
        industry = Industry(**validated_data)
        industry.save()
        return industry

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.logo = validated_data.get('logo', instance.logo)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.description = validated_data.get('description', instance.description)
        instance.supported = validated_data.get('supported', instance.supported)
        instance.save()
        return instance


class PublicIndustrySerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    industry_slug = serializers.CharField(max_length=100, min_length=3)
    logo = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()
    company_count = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance['company_count'] = instance['company__count']
        instance = super().to_representation(instance)
        return instance


class ComapnyIndustrySerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    industry_slug = serializers.CharField(max_length=100, min_length=3)


class BenefitSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    logo = serializers.CharField(max_length=200, required=False)
    icon = serializers.CharField(max_length=50, required=False)
    supported = serializers.BooleanField(default=True)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        benefit = Benefit(**validated_data)
        benefit.save()
        return benefit

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.logo = validated_data.get('logo', instance.logo)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.supported = validated_data.get('supported', instance.supported)
        instance.save()
        return instance


class UserBenefitSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    logo = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()


class GallerySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    path = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False)
    is_deleted = serializers.BooleanField(default=False)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo


class UserGallerySerializer(serializers.Serializer):
    path = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, allow_blank=True)


class ProvinceSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=50, min_length=2)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    supported = serializers.BooleanField(default=True)
    is_deleted = serializers.BooleanField(default=False)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        province = Province(**validated_data)
        province.save()
        return province

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.supported = validated_data.get('supported', instance.supported)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.save()
        return instance


class UserProvinceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, min_length=2)


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=50, min_length=2)
    city_slug = serializers.ReadOnlyField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    supported = serializers.BooleanField(default=True)
    province = UserProvinceSerializer()
    show_name = serializers.ReadOnlyField()
    is_deleted = serializers.BooleanField(default=False)
    priority = serializers.IntegerField(default=0)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['province'] = Province.objects.get(name=validated_data['province']['name'])
        validated_data['show_name'] = validated_data['name'] + ', ' + validated_data['province'].name
        validated_data['city_slug'] = utilities.slug_helper(validated_data['name'])
        city = City(**validated_data)
        city.save()
        return city

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get('province'):
            if validated_data.get('province')['id'] != instance.province.id:
                instance.province = Province.objects.get(id=validated_data.get('province')['id'])
                instance.show_name = instance.name + ', ' + instance.province.name
        if validated_data.get('name'):
            if validated_data.get('name') != instance.name:
                instance.name = validated_data.get('name')
                instance.show_name = instance.name + ', ' + instance.province.show_name

        instance.name = validated_data.get('name', instance.name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.supported = validated_data.get('supported', instance.supported)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.save()
        return instance


class UserCitySerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    show_name = serializers.ReadOnlyField()
    city_slug = serializers.CharField(max_length=50)


class ApproveCompaniesSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class CompanySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    name_en = serializers.CharField(max_length=100, min_length=2)
    description = serializers.CharField(max_length=3000, required=False)
    logo = serializers.CharField(max_length=200, required=False)
    cover = serializers.CharField(max_length=200, required=False)
    industry = ComapnyIndustrySerializer()
    founded = serializers.DateField(required=False)
    benefit = BenefitSerializer(many=True, required=False)
    gallery = serializers.ListField(child=GallerySerializer(), max_length=20, required=False)
    size = serializers.ChoiceField(choices=settings.OFFICE_SIZE_CHOICES)
    company_slug = serializers.CharField(max_length=100, min_length=2)
    is_deleted = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    updated = serializers.ReadOnlyField()
    city = UserCitySerializer()
    tell = serializers.CharField(max_length=14, min_length=10, required=False)
    site = serializers.CharField(max_length=100, min_length=5, required=False)
    location = serializers.ListField(child=serializers.DecimalField(max_digits=7, decimal_places=5), max_length=2,
                                     required=False)
    working_hours_start = serializers.TimeField(required=False)
    working_hours_stop = serializers.TimeField(required=False)
    approved = serializers.BooleanField(required=False)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    def validate_cover(self, cover):
        utilities.check_file_exist(cover)
        return cover

    def validate_site(self, site):
        urls = re.findall(settings.WEB_URL_REGEX, site)
        if not urls:
            raise serializers.ValidationError([{'site': 'Not a valid url'}])

        if site.startswith('http://') or site.startswith('https://'):
            return site
        else:
            return 'http://' + site

    def validate_company_slug(self, company_slug):
        if utilities.is_slug(company_slug):
            return company_slug
        raise serializers.ValidationError([{'company_slug': 'Not valid slug'}])

    def to_representation(self, instance):
        instance.created = instance.created.strftime('%Y-%m-%d')  # TODO check need this or not for better way to handle
        instance.gallery = instance.gallery_set.filter(is_deleted=False).all()
        if instance.location_point:
            instance.location = json.loads(instance.location_point.geojson)['coordinates']
        else:
            instance.location = [0, 0]
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        if data.get('benefit'):
            for benefit_data in data['benefit']:
                benefit = Benefit.objects.filter(name=benefit_data['name'].strip())
                if not benefit:
                    benefit = Benefit(name=benefit_data['name'].strip())
                    benefit.save()
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['industry'] = Industry.objects.get(industry_slug=validated_data['industry']['industry_slug'])
        if validated_data.get('gallery'):
            gallery = validated_data.pop('gallery')
        else:
            gallery = []
        if validated_data.get('benefit'):
            benefit = validated_data.pop('benefit')
        else:
            benefit = []
        validated_data['user'] = self.context['request'].user
        validated_data['city'] = City.objects.get(city_slug=validated_data['city']['city_slug'])
        validated_data['approved'] = True
        if validated_data.get('location_point'):
            validated_data['location_point'] = Point(validated_data.pop('location'))
        company = Company(**validated_data)
        company.save()
        for item in benefit:
            benefit_item = Benefit.objects.get(name=item['name'].strip())
            company.benefit.add(benefit_item)
        for item in gallery:
            item['company'] = company
            gallery_item = Gallery(**item)
            gallery_item.save()
        cache.delete(settings.COMPANY_NAME_LIST)
        return company

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.logo = validated_data.get('logo', instance.logo)
        instance.cover = validated_data.get('cover', instance.cover)
        instance.size = validated_data.get('size', instance.size)
        if validated_data.get('industry'):
            new_industry = Industry.objects.get(industry_slug=validated_data['industry']['industry_slug'])
            instance.industry = new_industry if instance.industry != new_industry else instance.industry
        instance.founded = validated_data.get('founded', instance.founded)
        if validated_data.get('benefit') is not None:
            instance.benefit.clear()
            for item in validated_data.get('benefit'):
                benefit_item = Benefit.objects.get(name=item['name'].strip())
                instance.benefit.add(benefit_item)
        if validated_data.get('city') and validated_data['city']['city_slug'] != instance.city.city_slug:
            instance.city = City.objects.get(id=validated_data['city']['city_slug'])
        instance.tell = validated_data.get('tell', instance.tell)
        instance.site = validated_data.get('site', instance.site)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours_start = validated_data.get('working_hours_start', instance.working_hours_start)
        instance.working_hours_stop = validated_data.get('working_hours_stop', instance.working_hours_stop)
        if validated_data.get('gallery'):
            instance.gallery_set.update(is_deleted=True)
            for gallery_data in validated_data['gallery']:
                if gallery_data.get('id'):  # Update gallery
                    gallery = Gallery.objects.get(id=gallery_data['id'])
                    gallery.path = gallery_data.get('path', gallery.path)
                    gallery.description = gallery_data.get('description', gallery.description)
                    gallery.save()
                else:
                    gallery_data['company'] = instance
                    gallery = Gallery(**gallery_data)
                    gallery.save()
        if validated_data.get('location'):
            instance.location_point = Point(validated_data.pop('location'))
        if validated_data.get('approved'):
            instance.approved = validated_data.pop('approved')
        instance.save()
        cache.delete(settings.COMPANY_NAME_LIST)
        return instance


class InsertCompanySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    description = serializers.CharField(max_length=3000, required=False)
    logo = serializers.CharField(max_length=200, required=False)
    gallery = serializers.ListField(child=GallerySerializer(), max_length=20, required=False)
    size = serializers.ChoiceField(choices=settings.OFFICE_SIZE_CHOICES)
    company_slug = serializers.CharField(max_length=100, min_length=2)
    industry = ComapnyIndustrySerializer()
    is_deleted = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    updated = serializers.ReadOnlyField()
    city = UserCitySerializer()
    tell = serializers.CharField(max_length=14, min_length=10, required=False)
    site = serializers.CharField(max_length=100, min_length=5, required=False)
    address = serializers.CharField(max_length=100, required=False)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    def validate_site(self, site):
        urls = re.findall(settings.WEB_URL_REGEX, site)
        if not urls:
            raise serializers.ValidationError([{'site': 'Not a valid url'}])

        if site.startswith('http://') or site.startswith('https://'):
            return site
        else:
            return 'http://' + site

    def validate_company_slug(self, company_slug):
        if utilities.is_slug(company_slug):
            return company_slug
        raise serializers.ValidationError([{'company_slug': 'Not valid slug'}])

    def to_representation(self, instance):
        instance.created = instance.created.strftime('%Y-%m-%d')
        instance.gallery = instance.gallery_set.filter(is_deleted=False).all()
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data['city']['city_slug'] = utilities.slug_helper(data['city']['name'])
        data['company_slug'] = utilities.slug_helper(data['name'])
        if data.get('size') is None:
            data['size'] = 'VS'
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        if validated_data.get('gallery'):
            gallery = validated_data.pop('gallery')
        else:
            gallery = []
        if len(Company.objects.filter(name=validated_data['name'])) > 0:
            raise CustomException(detail=ugettext('Company with this name exists.'))
        try:
            validated_data['city'] = City.objects.get(city_slug=validated_data['city']['city_slug'])
        except City.DoesNotExist as e:
            raise CustomException(detail=ugettext('City with this name does not exist.'))
        try:
            validated_data['industry'] = Industry.objects.get(industry_slug=validated_data['industry']['industry_slug'])
        except Industry.DoesNotExist as e:
            raise CustomException(detail=ugettext('Industry with this slug does not exist.'))
        validated_data['user'] = self.context['request'].user
        if validated_data.get('site'):
            validated_data['site'] = self.validate_site(validated_data['site'])
        validated_data['logo'] = self.validate_logo(validated_data['logo'])
        validated_data['approved'] = False
        company = Company(**validated_data)
        company.save()
        for item in gallery:
            item['company'] = company
            gallery_item = Gallery(**item)
            gallery_item.save()
        cache.delete(settings.COMPANY_NAME_LIST)
        return company


class UserInsertCompanySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    name_en = serializers.CharField(max_length=100, min_length=2)
    description = serializers.CharField(max_length=3000, required=False)
    logo = serializers.CharField(max_length=200, required=False)
    gallery = serializers.ListField(child=GallerySerializer(), max_length=20, required=False)
    size = serializers.ChoiceField(choices=settings.OFFICE_SIZE_CHOICES)
    company_slug = serializers.CharField(max_length=100, min_length=2)
    industry = ComapnyIndustrySerializer()
    is_deleted = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    updated = serializers.ReadOnlyField()
    city = UserCitySerializer()
    tell = serializers.CharField(max_length=14, min_length=10, required=False)
    site = serializers.CharField(max_length=100, min_length=5, required=False)
    address = serializers.CharField(max_length=100, required=False)

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    def validate_site(self, site):
        urls = re.findall(settings.WEB_URL_REGEX, site)
        if not urls:
            raise serializers.ValidationError([{'site': 'Not a valid url'}])

        if site.startswith('http://') or site.startswith('https://'):
            return site
        else:
            return 'http://' + site

    def validate_company_slug(self, company_slug):
        if utilities.is_slug(company_slug):
            return utilities.check_slug_available(Company, 'company_slug', company_slug)
        raise serializers.ValidationError([{'company_slug': 'Not valid slug'}])

    def to_representation(self, instance):
        instance.created = instance.created.strftime('%Y-%m-%d')  # TODO check need this or not for better way to handle
        instance.gallery = instance.gallery_set.filter(is_deleted=False).all()
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        if data.get('city') and not data['city'].get('city_slug') and data['city'].get('name'):
            data['city']['city_slug'] = utilities.slug_helper(data['city']['name'])
        data['company_slug'] = utilities.slug_helper(data['name_en'])
        if data.get('size') is None:
            data['size'] = 'VS'
        data = super().to_internal_value(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        if validated_data.get('gallery'):
            gallery = validated_data.pop('gallery')
        else:
            gallery = []
        if len(Company.objects.filter(name=validated_data['name'])) > 0:
            raise CustomException(detail=ugettext('Company with this name exists.'))
        try:
            validated_data['city'] = City.objects.get(city_slug=validated_data['city']['city_slug'])
        except City.DoesNotExist as e:
            raise CustomException(detail=ugettext('City with this name does not exist.'))
        try:
            validated_data['industry'] = Industry.objects.get(industry_slug=validated_data['industry']['industry_slug'])
        except Industry.DoesNotExist as e:
            raise CustomException(detail=ugettext('Industry with this slug does not exist.'))
        validated_data['user'] = self.context['request'].user
        if validated_data.get('site'):
            validated_data['site'] = self.validate_site(validated_data['site'])
        validated_data['logo'] = self.validate_logo(validated_data['logo'])
        validated_data['approved'] = False
        validated_data['user_generated'] = True
        company = Company(**validated_data)
        company.save()
        for item in gallery:
            item['company'] = company
            gallery_item = Gallery(**item)
            gallery_item.save()
        cache.delete(settings.COMPANY_NAME_LIST)
        return company


class UserCompanySerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    name_en = serializers.ReadOnlyField()
    logo = serializers.ReadOnlyField()
    cover = serializers.ReadOnlyField()
    industry = ComapnyIndustrySerializer()
    founded = serializers.ReadOnlyField()
    benefit = UserBenefitSerializer(many=True)
    gallery = serializers.ListField(child=UserGallerySerializer())
    company_slug = serializers.ReadOnlyField()
    city = UserCitySerializer()
    size = serializers.ReadOnlyField()
    site = serializers.ReadOnlyField()
    tell = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    total_interview = serializers.ReadOnlyField()
    total_companyview = serializers.ReadOnlyField()
    location = serializers.ReadOnlyField()
    salary_avg = serializers.ReadOnlyField()
    salary_min = serializers.ReadOnlyField()
    salary_max = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    seconds_to_next_review = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    # review_result = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.founded = instance.founded.strftime('%Y') if instance.founded else 'سال نامشخص'
        instance.view_count = instance.view.count() + instance.total_view
        instance.total_companyview = instance.total_review
        instance.total_review = instance.total_review + instance.total_interview
        if isinstance(self.context['request'].user, User):
            has_review = instance.companyreview_set.filter(creator=self.context['request'].user)
            instance.seconds_to_next_review = -round((datetime.now() - (has_review.last().created + timedelta(days=90))).total_seconds()) if has_review else 0
        else:
            instance.seconds_to_next_review = 0
        if instance.has_legal_issue:
            is_deleted_text = settings.IS_DELETED_TEXT % instance.name
            instance.gallery = []
            instance.description = is_deleted_text
            instance.salary_min = 0
            instance.salary_max = 0
            instance.over_all_rate = 0
            instance.salary_avg = 0
            instance.cover = 'https://media.jobguy.work/default/company/header.jpg'
            instance.tell = is_deleted_text
            instance.location = [0, 0]
        else:
            instance.gallery = instance.gallery_set.filter(is_deleted=False).all()
            if instance.location_point:
                instance.location = json.loads(instance.location_point.geojson)['coordinates']
            else:
                instance.location = [0, 0]
        instance = super().to_representation(instance)
        return instance


class PublicCompanyListSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    company_slug = serializers.ReadOnlyField()
    founded = serializers.DateField(required=False)
    logo = serializers.ReadOnlyField()
    city = UserCitySerializer()
    description = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    total_interview = serializers.ReadOnlyField()
    total_companyreview = serializers.ReadOnlyField()
    salary_min = serializers.ReadOnlyField()
    salary_max = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance['founded'] = instance['founded'].strftime('%Y') if instance['founded'] else 'سال نامشخص'
        instance['total_companyreview'] = instance['total_review']
        instance['total_review'] = instance['total_review'] + instance['total_interview']
        if instance['has_legal_issue']:
            is_deleted_text = settings.IS_DELETED_TEXT % instance['name']
            instance['gallery'] = []
            instance['description'] = is_deleted_text
            instance['salary_min'] = 0
            instance['salary_max'] = 0
            instance['over_all_rate'] = 0
        else:
            if instance.get('description'):
                if len(instance['description']) > 180:
                    instance['description'] = ' '.join(instance['description'][:180].split(' ')[:-1]) + ' ...'

            else:
                instance['description'] = ''
        instance['city'] = {
            'name': instance['city__name'],
            'show_name': instance['city__show_name'],
            'city_slug': instance['city__city_slug'],
        }
        instance = super().to_representation(instance)
        return instance


class CompanyNameListSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    name_en = serializers.ReadOnlyField()
    company_slug = serializers.ReadOnlyField()


class PublicUserCompanySerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    name_en = serializers.ReadOnlyField()
    company_slug = serializers.CharField(max_length=255)
    logo = serializers.ReadOnlyField()
