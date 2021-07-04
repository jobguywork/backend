from django.db import transaction
from rest_framework import serializers

from question.models import Question, Answer
from company.models import Company
from company.serializers import PublicUserCompanySerializer
from utilities import utilities


class PublicAnswerSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    body = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance


class UserQuestionSerializer(serializers.Serializer):
    question_slug = serializers.CharField(max_length=100)


class QuestionSerializer(serializers.Serializer):
    company = PublicUserCompanySerializer()
    title = serializers.CharField(max_length=100, min_length=5)
    body = serializers.CharField(max_length=1000, min_length=10)
    created = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    question_slug = serializers.ReadOnlyField()
    answer_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()

    @transaction.atomic
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['company'] = Company.objects.get(company_slug=validated_data['company']['company_slug'])
        validated_data['question_slug'] = utilities.check_slug_available(Question, 'question_slug',
                                                                         utilities.slug_helper(validated_data['title'])
                                                                         + '-{}'.format(validated_data['company'].company_slug))
        question = Question(**validated_data)
        question.save()
        utilities.telegram_notify('New Question: on {}, \n {}'.format(
            question.company.name, '#question'
        ), question.id, 'question', question.title, question.body)
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        utilities.telegram_notify('Update Question: on {}, \n {}'.format(
            instance.company.name, '#update_question'
        ), instance.id, 'question', instance.title, instance.body)
        return instance

    def to_representation(self, instance):
        # instance.answer = instance.answer_set.all()
        instance.answer_count = instance.answer_set.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data


class AnswerSerializer(serializers.Serializer):
    question = UserQuestionSerializer()
    body = serializers.CharField(max_length=5000, min_length=10)
    created = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()

    @transaction.atomic
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['question'] = Question.objects.get(question_slug=validated_data['question']['question_slug'])
        answer = Answer(**validated_data)
        answer.save()
        utilities.telegram_notify('New Answer: on {}, \n {}'.format(
            answer.question.company.name, '#answer'
        ), answer.id, 'answer', None, answer.body)
        return answer

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        utilities.telegram_notify('Update Answer: on {}, \n {}'.format(
            instance.question.company.name, '#update_answer'
        ), instance.id, 'answer', None, instance.body)
        return instance

    def to_representation(self, instance):
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data


class PublicQuestionSerializer(serializers.Serializer):
    company = PublicUserCompanySerializer()
    title = serializers.CharField(max_length=100, min_length=5)
    body = serializers.CharField(max_length=1000, min_length=10)
    created = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    down_vote_count = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    question_slug = serializers.ReadOnlyField()
    answers = PublicAnswerSerializer(many=True)
    answer_count = serializers.ReadOnlyField()
    vote_state = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance.answers = instance.answer_set.all()
        instance.answer_count = instance.answer_set.count()
        instance.vote_count = instance.vote.count()
        instance.down_vote_count = instance.down_vote.count()
        instance.vote_state = utilities.check_vote_status(instance, self.context['request'].user)
        instance.view_count = instance.view.count() + instance.total_view
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        return instance
