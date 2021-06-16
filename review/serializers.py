import re
from datetime import date, datetime

from django.db import transaction
from django.db.models import Q
from django.conf import settings
from rest_framework import serializers
from bs4 import BeautifulSoup

from review.models import Pros, Cons, CompanyReview, Interview, ReviewComment, InterviewComment
from review.permissions import (check_create_company_review_permission, check_create_interview_permission,
                                check_create_review_comment_permission, check_create_interview_comment_permission)
from company.models import Company
from job.models import Job
from company.serializers import PublicUserCompanySerializer
from job.serializers import PublicUserJobSerializer
from review import utilities as review_utilities
from utilities import utilities


class ProsSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    icon = serializers.CharField(max_length=50, required=False)
    logo = serializers.CharField(max_length=200, required=False)
    is_deleted = serializers.ReadOnlyField()

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    @transaction.atomic
    def create(self, validated_data):
        pros = Pros(**validated_data)
        pros.save()
        return pros

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.icon = validated_data.get('icon', instance.icon)
        instance.save()
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance


class UserProsSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()
    logo = serializers.ReadOnlyField()
    priority = serializers.ReadOnlyField()


class ConsSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=100, min_length=2)
    icon = serializers.CharField(max_length=50, required=False)
    logo = serializers.CharField(max_length=200, required=False)
    is_deleted = serializers.ReadOnlyField()

    def validate_logo(self, logo):
        utilities.check_file_exist(logo)
        return logo

    @transaction.atomic
    def create(self, validated_data):
        cons = Cons(**validated_data)
        cons.save()
        return cons

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.icon = validated_data.get('icon', instance.icon)
        instance.save()
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance


class UserConsSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()
    logo = serializers.ReadOnlyField()
    priority = serializers.ReadOnlyField()


class CompanyReviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    recommend_to_friend = serializers.BooleanField()
    pros = ProsSerializer(many=True, required=False)
    cons = ConsSerializer(many=True, required=False)
    state = serializers.ChoiceField(choices=settings.STATE_CHOICES)
    # ratings
    work_life_balance = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    salary_benefit = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    security = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    management = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    culture = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    title = serializers.CharField(max_length=100)
    anonymous_job = serializers.BooleanField(default=False)
    description = serializers.CharField(max_length=40000, required=False, allow_blank=True)
    salary = serializers.IntegerField()
    salary_type = serializers.ChoiceField(choices=CompanyReview.SALARY_CHOICES)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    current_work = serializers.BooleanField(default=False)
    is_deleted = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    creator_data = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    reply = serializers.ReadOnlyField()
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def validate(self, data):
        if data.get('salary'):
            salary = review_utilities.salary_handler(data['salary'], data['salary_type'])
            if salary > 50000000:  # 50 million toman
                raise serializers.ValidationError({'salary': ['Max Salary in month is 50 million toman :(.']})
        if data.get('pros') and len(data['pros']) > 20:
            raise serializers.ValidationError({'pros': ['Pros list must len 0, 20 item']})
        if data.get('cons') and len(data['cons']) > 20:
            raise serializers.ValidationError({'cons': ['Cons list must len 0, 20 item']})
        if data.get('start_date') and date.today() < data['start_date']:
            raise serializers.ValidationError({'start_date': ['Start date must be lower than today']})
        if data.get('start_date') and data.get('end_date') and data['end_date'] < data['start_date']:
            raise serializers.ValidationError({'end_date': ['End date must be greater than start date']})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['company'] = Company.objects.get(company_slug=validated_data['company']['company_slug'])
        validated_data['creator'] = self.context['request'].user
        check_create_company_review_permission(validated_data['creator'], validated_data['company'])
        if validated_data.get('pros') is not None:
            pros_list = validated_data.pop('pros')
        else:
            pros_list = []
        if validated_data.get('cons') is not None:
            cons_list = validated_data.pop('cons')
        else:
            cons_list = []
        if validated_data.get('description') is not None and not validated_data['description'].split():  # blank checking
            validated_data.pop('description')
        validated_data['job'] = Job.objects.get(job_slug=validated_data['job']['job_slug'])

        validated_data['salary'] = review_utilities.salary_handler(validated_data['salary'], validated_data['salary_type'])
        validated_data['over_all_rate'] = round((validated_data['work_life_balance'] + validated_data['salary_benefit']
                                                 + validated_data['security'] + validated_data['management'] +
                                                 validated_data['culture']) / 5, 1)
        validated_data['ip'] = utilities.get_client_ip(self.context['request'])
        validated_data['approved'] = False
        company_review = CompanyReview(**validated_data)
        company_review.save()
        for pros_data in pros_list:
            pros = Pros.objects.get(name=pros_data['name'])
            company_review.pros.add(pros)
            pros.add_cons_priority()
        for cons_data in cons_list:
            cons = Cons.objects.get(name=cons_data['name'])
            company_review.cons.add(cons)
            cons.add_cons_priority()
        validated_data['company'].handle_company_review_statics()
        utilities.telegram_notify('New review: on {}, \n {}'.format(
            company_review.company.name, '#review'
        ), company_review.id, 'review', company_review.title, company_review.description)

        return company_review

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.recommend_to_friend = validated_data.get('recommend_to_friend', instance.recommend_to_friend)
        instance.state = validated_data.get('state', instance.state)
        instance.work_life_balance = validated_data.get('work_life_balance', instance.work_life_balance)
        instance.salary_benefit = validated_data.get('salary_benefit', instance.salary_benefit)
        instance.security = validated_data.get('security', instance.security)
        instance.management = validated_data.get('management', instance.management)
        instance.culture = validated_data.get('culture', instance.culture)
        instance.anonymous_job = validated_data.get('anonymous_job', instance.anonymous_job)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.current_work = validated_data.get('current_work', instance.current_work)
        instance.over_all_rate = (instance.work_life_balance + instance.salary_benefit + instance.security +
                                  instance.management + instance.culture) / 5
        if (validated_data.get('salary', None) is not None and validated_data['salary'] != instance.salary) or\
                (validated_data.get('salary_type') and validated_data['salary_type'] != instance.salary_type):
            instance.salary = review_utilities.salary_handler(validated_data['salary'], validated_data['salary_type'])
            instance.salary_type = validated_data.get('salary_type', instance.salary_type)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        if validated_data.get('pros'):
            instance.pros.clear()
            for pros_data in validated_data['pros']:
                pros = Pros.objects.get(name=pros_data['name'])
                instance.pros.add(pros)
                pros.add_cons_priority()

        if validated_data.get('cons'):
            instance.cons.clear()
            for cons_data in validated_data['cons']:
                cons = Cons.objects.get(name=cons_data['name'])
                instance.cons.add(cons)
                cons.add_cons_priority()

        if validated_data.get('job') and instance.job.name != validated_data['job']['name']:
            instance.job = Job.objects.get(job_slug=validated_data['job']['job_slug'])
        instance.save()
        instance.company.handle_company_review_statics()
        utilities.telegram_notify('Update Review: on {}, \n {}'.format(
            instance.company.name, '#update_review'
        ), instance.id, 'review', instance.title, instance.description)
        return instance

    def to_internal_value(self, data):
        if data.get('pros'):
            for pros_data in data['pros']:
                pros = Pros.objects.filter(name=pros_data['name'].strip())
                if not pros:
                    pros = Pros(name=pros_data['name'].strip())
                    pros.save()
        if data.get('cons'):
            for cons_data in data.get('cons'):
                cons = Cons.objects.filter(name=cons_data['name'].strip())
                if not cons:
                    cons = Cons(name=cons_data['name'].strip())
                    cons.save()
        if data.get('job'):
            job = Job.objects.filter(Q(name=data['job']['name'].strip()) |
                                     Q(job_slug='-'.join(re.findall('[\w-]+', data['job']['name'].strip())).lower()))
            if not job:
                job = Job(name=data['job']['name'].strip(),
                          job_slug='-'.join(re.findall('[\w-]+', data['job']['name'].strip())).lower())
                job.save()
            else:
                job = job[0]
            data['job']['job_slug'] = job.job_slug
        data = super().to_internal_value(data)
        return data

    def to_representation(self, instance):
        instance.creator_data = {'name': instance.creator.username}
        instance.salary = round(review_utilities.salary_handler(instance.salary,
                                                                instance.salary_type, resp=True)/100000)/10
        self.fields['salary'] = serializers.FloatField()
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.start_date = instance.start_date.strftime('%Y-%m') if instance.start_date else 'نامشخص'
        instance.end_date = instance.end_date.strftime('%Y-%m') if instance.end_date else 'نامشخص'
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        return instance


class UserCompanyReviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    recommend_to_friend = serializers.BooleanField()
    pros = UserProsSerializer(many=True)
    cons = UserConsSerializer(many=True)
    state = serializers.ReadOnlyField()
    # ratings
    work_life_balance = serializers.ReadOnlyField()
    salary_benefit = serializers.ReadOnlyField()
    security = serializers.ReadOnlyField()
    management = serializers.ReadOnlyField()
    culture = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    salary = serializers.ReadOnlyField()
    salary_type = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    start_date = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    current_work = serializers.ReadOnlyField()
    anonymous_job = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    reply = serializers.ReadOnlyField()
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def to_representation(self, instance):
        if self.context['request'].user != instance.creator and instance.anonymous_job:
            instance.job = Job(name='تخصص مخفی', job_slug='')

        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.over_all_rate = round((instance.work_life_balance + instance.salary_benefit +
                                        instance.security + instance.management + instance.culture) / 5, 1)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.start_date = instance.start_date.strftime('%Y-%m-%d') if instance.start_date else 'نامشخص'
        instance.end_date = instance.end_date.strftime('%Y-%m-%d') if instance.end_date else 'نامشخص'
        instance.reply_created = instance.reply_created.strftime('%Y-%m-%d %H:%M') if instance.reply_created else None
        if instance.description is None:
            instance.description = ''
        instance.comment_count = instance.reviewcomment_set.count()
        if instance.has_legal_issue:
            is_deleted_text = settings.IS_DELETED_TEXT % instance.company.name
            instance.title = is_deleted_text
            instance.description = is_deleted_text
            instance.work_life_balance = 0
            instance.salary_benefit = 0
            instance.security = 0
            instance.management = 0
            instance.culture = 0
            instance.salary = 0
        else:
            instance.salary = round(review_utilities.salary_handler(instance.salary, instance.salary_type, resp=True))
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        if instance['has_legal_issue']:
            instance['pros'] = []
            instance['cons'] = []
        return instance


class UserCompanyReviewListSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    # ratings
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    state = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()

    def to_representation(self, instance):
        if instance.anonymous_job:
            instance.job = Job(name='تخصص مخفی', job_slug='')
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.over_all_rate = round((instance.work_life_balance + instance.salary_benefit +
                                        instance.security + instance.management + instance.culture) / 5, 1)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        if instance.has_legal_issue:
            is_deleted_text = settings.IS_DELETED_TEXT % instance.company.name
            instance.title = is_deleted_text
            instance.description = is_deleted_text
            instance.over_all_rate = 0
            instance.salary = 0
        else:
            if instance.description:
                instance.description = instance.description.replace('<br>', '<br>\n')
                soup = BeautifulSoup(instance.description, 'html.parser')
                body = soup.get_text()
                if len(body) > 300:
                    instance.description = ' '.join(body[:300].split(' ')[:-1]) + ' ...'
                else:
                    instance.description = body
            else:
                instance.description = ''
        instance = super().to_representation(instance)
        return instance


class UserHomeCompanyReviewListSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    # ratings
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance['company'] = {
            'name': instance['company__name'],
            'name_en': instance['company__name_en'],
            'company_slug': instance['company__company_slug'],
            'logo': instance['company__logo'],
        }
        instance['created'] = instance['created'].strftime('%Y-%m-%d %H:%M')
        instance['my_review'] = instance['creator'] == self.context['request'].user.id
        if instance['has_legal_issue']:
            is_deleted_text = settings.IS_DELETED_TEXT % instance['company']['name']
            instance['title'] = is_deleted_text
            instance['description'] = is_deleted_text
            instance['over_all_rate'] = 0
        else:
            if instance['description']:
                instance['description'] = instance['description'].replace('<br>', '<br>\n')
                soup = BeautifulSoup(instance['description'], 'html.parser')
                body = soup.get_text()
                if len(body) > 300:
                    instance['description'] = ' '.join(body[:300].split(' ')[:-1]) + ' ...'
                else:
                    instance['description'] = body
            else:
                instance['description'] = ''

        instance = super().to_representation(instance)
        return instance


class InterviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    pros = ProsSerializer(many=True, required=False)
    cons = ConsSerializer(many=True, required=False)
    status = serializers.ChoiceField(choices=settings.INTERVIEW_STATUS)
    apply_method = serializers.ChoiceField(choices=settings.APPLY_METHOD)
    # ratings
    interviewer_rate = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    total_rate = serializers.ChoiceField(choices=settings.RATE_CHOICES)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=40000, required=False, allow_blank=True)
    asked_salary = serializers.IntegerField()
    offered_salary = serializers.IntegerField()
    interview_date = serializers.DateField()
    response_time_before_review = serializers.ChoiceField(Interview.RESPONSE_TIME_CHOICES)
    response_time_after_review = serializers.ChoiceField(Interview.RESPONSE_TIME_CHOICES, required=False)
    is_deleted = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    creator_data = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    reply = serializers.ReadOnlyField()
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def validate(self, data):
        if data.get('offered_salary'):
            if data.get('offered_salary') > 50000000:  # 50 million toman
                raise serializers.ValidationError({'offered_salary': ['Max Salary in month is 50 million toman :(.']})
        if data.get('asked_salary'):
            if data.get('asked_salary') > 50000000:  # 50 million toman
                raise serializers.ValidationError({'asked_salary': ['Max Salary in month is 50 million toman :(.']})
        if data.get('pros') and len(data['pros']) > 20:
            raise serializers.ValidationError({'pros': ['Pros list must len 0, 20 item']})
        if data.get('cons') and len(data['cons']) > 20:
            raise serializers.ValidationError({'cons': ['Cons list must len 0, 20 item']})
        if data.get('interview_date') and date.today() < data['interview_date']:
            raise serializers.ValidationError({'start_date': ['Interview date must be lower than today']})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['company'] = Company.objects.get(company_slug=validated_data['company']['company_slug'])
        validated_data['creator'] = self.context['request'].user
        check_create_interview_permission(validated_data['creator'], validated_data['company'])
        if validated_data.get('pros') is not None:
            pros_list = validated_data.pop('pros')
        else:
            pros_list = []
        if validated_data.get('cons') is not None:
            cons_list = validated_data.pop('cons')
        else:
            cons_list = []
        if validated_data.get('description') is not None and not validated_data['description'].split():  # blank checking
            validated_data.pop('description')
        validated_data['job'] = Job.objects.get(job_slug=validated_data['job']['job_slug'])
        validated_data['asked_salary'] = validated_data['asked_salary']
        validated_data['offered_salary'] = validated_data['offered_salary']
        validated_data['ip'] = utilities.get_client_ip(self.context['request'])
        validated_data['approved'] = False
        interview = Interview(**validated_data)
        interview.save()
        for pros_data in pros_list:
            pros = Pros.objects.get(name=pros_data['name'])
            interview.pros.add(pros)
            pros.add_cons_priority()
        for cons_data in cons_list:
            cons = Cons.objects.get(name=cons_data['name'])
            interview.cons.add(cons)
            cons.add_cons_priority()
        validated_data['company'].handle_company_interview_statics()
        utilities.telegram_notify('New interview: on {}, \n {}'.format(
            interview.company.name, '#interview'
        ), interview.id, 'interview', interview.title, interview.description)
        return interview

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.apply_method = validated_data.get('apply_method', instance.apply_method)
        instance.interviewer_rate = validated_data.get('interviewer_rate', instance.interviewer_rate)
        instance.total_rate = validated_data.get('total_rate', instance.total_rate)
        instance.interview_date = validated_data.get('interview_date', instance.interview_date)
        instance.response_time_before_review = validated_data.get('response_time_before_review',
                                                                  instance.response_time_before_review)
        instance.response_time_after_review = validated_data.get('response_time_after_review',
                                                                 instance.response_time_after_review)

        if validated_data.get('job') and instance.job.name != validated_data['job']['name']:
            instance.job = Job.objects.get(job_slug=validated_data['job']['job_slug'])

        if validated_data.get('asked_salary', None) is not None and validated_data['asked_salary'] != instance.asked_salary:
            instance.asked_salary = validated_data['asked_salary']
        if validated_data.get('offered_salary', None) is not None and validated_data['offered_salary'] != instance.offered_salary:
            instance.offered_salary = validated_data['offered_salary']

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        if validated_data.get('pros'):
            instance.pros.clear()
            for pros_data in validated_data['pros']:
                pros = Pros.objects.get(name=pros_data['name'])
                instance.pros.add(pros)
                pros.add_cons_priority()

        if validated_data.get('cons'):
            instance.cons.clear()
            for cons_data in validated_data['cons']:
                cons = Cons.objects.get(name=cons_data['name'])
                instance.cons.add(cons)
                cons.add_cons_priority()

        instance.save()
        instance.company.handle_company_interview_statics()
        utilities.telegram_notify('Update Interview: on {}, \n  {}'.format(
            instance.company.name, '#update_interview'
        ), instance.id, 'interview', instance.title, instance.description)
        return instance

    def to_internal_value(self, data):
        if data.get('pros'):
            for pros_data in data['pros']:
                pros = Pros.objects.filter(name=pros_data['name'].strip())
                if not pros:
                    pros = Pros(name=pros_data['name'].strip())
                    pros.save()
        if data.get('cons'):
            for cons_data in data.get('cons'):
                cons = Cons.objects.filter(name=cons_data['name'].strip())
                if not cons:
                    cons = Cons(name=cons_data['name'].strip())
                    cons.save()
        if data.get('job'):
            job = Job.objects.filter(Q(name=data['job']['name'].strip()) |
                                     Q(job_slug='-'.join(re.findall('[\w-]+', data['job']['name'].strip())).lower()))
            if not job:
                job = Job(name=data['job']['name'].strip(),
                          job_slug='-'.join(re.findall('[\w-]+', data['job']['name'].strip())).lower())

                job.save()
            else:
                job = job[0]
            data['job']['job_slug'] = job.job_slug
        data = super().to_internal_value(data)
        return data

    def to_representation(self, instance):
        instance.creator_data = {'name': instance.creator.username}
        instance.offered_salary = round(instance.offered_salary/100000)/10
        self.fields['offered_salary'] = serializers.FloatField()
        instance.asked_salary = round(instance.asked_salary/100000)/10
        self.fields['asked_salary'] = serializers.FloatField()
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.interview_date = instance.interview_date.strftime('%Y-%m') if instance.interview_date else 'نامشخص'
        instance.reply_created = instance.reply_created.strftime('%Y-%m-%d %H:%M') if instance.reply_created else None
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        return instance


class UserInterviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    pros = UserProsSerializer(many=True)
    cons = UserConsSerializer(many=True)
    status = serializers.ReadOnlyField()
    apply_method = serializers.ReadOnlyField()
    interviewer_rate = serializers.ReadOnlyField()
    total_rate = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    asked_salary = serializers.ReadOnlyField()
    offered_salary = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    interview_date = serializers.ReadOnlyField()
    response_time_before_review = serializers.ReadOnlyField()
    response_time_after_review = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    reply = serializers.ReadOnlyField()
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.interview_date = instance.interview_date.strftime('%Y-%m-%d') if instance.interview_date else 'نامشخص'
        instance.reply_created = instance.reply_created.strftime('%Y-%m-%d %H:%M') if instance.reply_created else None
        if instance.description is None:
            instance.description = ''
        instance.asked_salary = instance.asked_salary
        instance.offered_salary = instance.offered_salary
        if instance.has_legal_issue:
            is_deleted_text = settings.IS_DELETED_TEXT % instance.company.name
            instance.title = is_deleted_text
            instance.description = is_deleted_text
            instance.interviewer_rate = 0
            instance.total_rate = 0
            instance.asked_salary = 0
            instance.offered_salary = 0
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        if instance['has_legal_issue']:
            instance['pros'] = []
            instance['cons'] = []
        return instance


class UserInterviewListSerializer(serializers.Serializer):
    interviewer_rate = serializers.ReadOnlyField()
    total_rate = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    job = PublicUserJobSerializer()
    # ratings
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        if instance.has_legal_issue:
            is_deleted_text = settings.IS_DELETED_TEXT % instance.company.name
            instance.title = is_deleted_text
            instance.description = is_deleted_text
            instance.interviewer_rate = 0
            instance.total_rate = 0
        else:
            if instance.description:
                instance.description = instance.description.replace('<br>', '<br>\n')
                soup = BeautifulSoup(instance.description, 'html.parser')
                body = soup.get_text()
                if len(body) > 300:
                    instance.description = ' '.join(body[:300].split(' ')[:-1]) + ' ...'
                else:
                    instance.description = body
            else:
                instance.description = ''

        instance = super().to_representation(instance)
        return instance


class UserHomeInterviewListSerializer(serializers.Serializer):
    total_rate = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    # ratings
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance['company'] = {
            'name': instance['company__name'],
            'name_en': instance['company__name_en'],
            'company_slug': instance['company__company_slug'],
            'logo': instance['company__logo'],
        }
        instance['created'] = instance['created'].strftime('%Y-%m-%d %H:%M')
        instance['my_review'] = instance['creator'] == self.context['request'].user.id
        if instance['has_legal_issue']:
            is_deleted_text = settings.IS_DELETED_TEXT % instance['company']['name']
            instance['title'] = is_deleted_text
            instance['description'] = is_deleted_text
            instance['total_rate'] = 0
        else:
            if instance['description']:
                instance['description'] = instance['description'].replace('<br>', '<br>\n')
                soup = BeautifulSoup(instance['description'], 'html.parser')
                body = soup.get_text()
                if len(body) > 300:
                    instance['description'] = ' '.join(body[:300].split(' ')[:-1]) + ' ...'
                else:
                    instance['description'] = body
            else:
                instance['description'] = ''

        instance = super().to_representation(instance)
        return instance


class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.ReadOnlyField()


class ReviewCommentSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=500)
    vote_state = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    review = ReviewSerializer()

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data['review'] = CompanyReview.objects.get(id=validated_data['review']['id'], is_deleted=False,
                                                                 approved=True)
        except CompanyReview.DoesNotExist as e:
            raise serializers.ValidationError({'review': ['review does not exist.']})

        validated_data['creator'] = self.context['request'].user
        check_create_review_comment_permission(validated_data['creator'], validated_data['review'])
        comment = ReviewComment(**validated_data)
        validated_data['ip'] = utilities.get_client_ip(self.context['request'])
        comment.save()
        utilities.telegram_notify('New Review Comment: {}'.format(
            '#review_comment'
        ), comment.id, 'review_comment', None, comment.body)
        return comment

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        utilities.telegram_notify('Update Review Comment: {}'.format(
            '#update_review_comment'
        ), instance.id, 'review_comment', None, instance.body)
        return instance

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance


class UserReviewCommentSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=500)
    vote_state = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance


class InterviewCommentSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=500)
    vote_state = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    interview = ReviewSerializer()

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data['interview'] = Interview.objects.get(id=validated_data['interview']['id'], is_deleted=False,
                                                                approved=True)
        except Interview.DoesNotExist as e:
            raise serializers.ValidationError({'interview': ['interview does not exist.']})

        validated_data['creator'] = self.context['request'].user
        check_create_interview_comment_permission(validated_data['creator'], validated_data['interview'])
        comment = InterviewComment(**validated_data)
        validated_data['ip'] = utilities.get_client_ip(self.context['request'])
        comment.save()
        utilities.telegram_notify('New Interview Comment: {}'.format(
            '#interview_comment'
        ), comment.id, 'interview_comment', None, comment.body)
        return comment

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        utilities.telegram_notify('Update Interview Comment: {}'.format(
            '#update_interview_comment'
        ), instance.id, 'interview_comment', None, instance.body)
        return instance

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance


class BotApproveReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=(
        ('review', 'review'),
        ('interview', 'interview'),
        ('question', 'question'),
        ('answer', 'answer'),
        ('review_comment', 'review_comment'),
        ('interview_comment', 'interview_comment'),
    ))
    approved = serializers.BooleanField()


class ReplyCompanyReviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer(read_only=True)
    job = PublicUserJobSerializer(read_only=True)
    recommend_to_friend = serializers.ReadOnlyField()
    pros = ProsSerializer(many=True, read_only=True)
    cons = ConsSerializer(many=True, read_only=True)
    state = serializers.ReadOnlyField()
    # ratings
    work_life_balance = serializers.ReadOnlyField()
    salary_benefit = serializers.ReadOnlyField()
    security = serializers.ReadOnlyField()
    management = serializers.ReadOnlyField()
    culture = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    anonymous_job = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    salary = serializers.ReadOnlyField()
    salary_type = serializers.ReadOnlyField()
    start_date = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    current_work = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    creator_data = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    reply = serializers.CharField(max_length=40000)
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def to_representation(self, instance):
        if self.context['request'].user != instance.creator and instance.anonymous_job:
            instance.job = Job(name='تخصص مخفی', job_slug='')

        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count()
        instance.total_view = instance.total_view
        instance.over_all_rate = round((instance.work_life_balance + instance.salary_benefit +
                                        instance.security + instance.management + instance.culture) / 5, 1)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.start_date = instance.start_date.strftime('%Y-%m-%d') if instance.start_date else 'نامشخص'
        instance.end_date = instance.end_date.strftime('%Y-%m-%d') if instance.end_date else 'نامشخص'
        if instance.description is None:
            instance.description = ''
        instance.comment_count = instance.reviewcomment_set.count()
        instance.salary = round(review_utilities.salary_handler(instance.salary, instance.salary_type, resp=True))
        instance.reply_created = instance.reply_created.strftime('%Y-%m-%d %H:%M') if instance.reply_created else None
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.reply = validated_data.get('reply', instance.reply)
        if not instance.reply_created:
            instance.reply_created = datetime.now()
        instance.save()
        return instance


class ReplyInterviewSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer(read_only=True)
    job = PublicUserJobSerializer(read_only=True)
    pros = UserProsSerializer(many=True, read_only=True)
    cons = UserConsSerializer(many=True, read_only=True)
    status = serializers.ReadOnlyField()
    apply_method = serializers.ReadOnlyField()
    interviewer_rate = serializers.ReadOnlyField()
    total_rate = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    asked_salary = serializers.ReadOnlyField()
    offered_salary = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    over_all_rate = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    my_review = serializers.ReadOnlyField()
    interview_date = serializers.ReadOnlyField()
    response_time_before_review = serializers.ReadOnlyField()
    response_time_after_review = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    reply = serializers.CharField(max_length=40000)
    reply_created = serializers.ReadOnlyField()
    total_review = serializers.ReadOnlyField()
    rate_avg = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count()
        instance.total_view = instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance.my_review = instance.creator == self.context['request'].user
        instance.interview_date = instance.interview_date.strftime('%Y-%m-%d') if instance.interview_date else 'نامشخص'
        if instance.description is None:
            instance.description = ''
        instance.asked_salary = instance.asked_salary
        instance.offered_salary = instance.offered_salary
        instance.reply_created = instance.reply_created.strftime('%Y-%m-%d %H:%M') if instance.reply_created else None
        instance.total_review = instance.creator.profile.total_review
        instance.rate_avg = instance.creator.profile.rate_avg
        instance = super().to_representation(instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.reply = validated_data.get('reply', instance.reply)
        if not instance.reply_created:
            instance.reply_created = datetime.now()
        instance.save()
        return instance


class UserHomeReviewListSerializer(serializers.Serializer):
    over_all_rate = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    company = PublicUserCompanySerializer()
    # ratings
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()
    has_legal_issue = serializers.ReadOnlyField()
    type = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance['company'] = {
            'name': instance['company__name'],
            'name_en': instance['company__name_en'],
            'company_slug': instance['company__company_slug'],
            'logo': instance['company__logo'],
        }
        instance['created'] = instance['created'].strftime('%Y-%m-%d %H:%M')
        instance['my_review'] = instance['creator'] == self.context['request'].user.id
        if instance['has_legal_issue']:
            is_deleted_text = settings.IS_DELETED_TEXT % instance['company']['name']
            instance['title'] = is_deleted_text
            instance['description'] = is_deleted_text
            instance['over_all_rate'] = 0
        else:
            if instance['description']:
                instance['description'] = instance['description'].replace('<br>', '<br>\n')
                soup = BeautifulSoup(instance['description'], 'html.parser')
                body = soup.get_text()
                if len(body) > 300:
                    instance['description'] = ' '.join(body[:300].split(' ')[:-1]) + ' ...'
                else:
                    instance['description'] = body
            else:
                instance['description'] = ''
        instance = super().to_representation(instance)
        return instance
