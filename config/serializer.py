from rest_framework import serializers

from config.models import IntegerConfig


class IntegerConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = IntegerConfig
        exclude = ('id',)
