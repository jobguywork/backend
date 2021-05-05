from django.db import transaction
from rest_framework import serializers

from job.models import Job
from utilities.utilities import slug_helper


class JobSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=50, min_length=3)
    job_slug = serializers.ReadOnlyField()
    cover = serializers.CharField(max_length=200, required=False)
    icon = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=10000, required=False)
    is_deleted = serializers.ReadOnlyField()
    approved = serializers.ReadOnlyField()

    @transaction.atomic
    def create(self, validated_data):
        validated_data['job_slug'] = slug_helper(validated_data['name'])
        job = Job(**validated_data)
        job.save()
        return job

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.cover = validated_data.get('cover', instance.cover)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return instance


class PublicJobSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, min_length=3)
    job_slug = serializers.ReadOnlyField()
    cover = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    company_count = serializers.ReadOnlyField()


class PublicUserJobSerializer(serializers.Serializer):
    job_slug = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50, min_length=3)
