from django.db import transaction
from rest_framework import serializers, exceptions

from donate.models import Donate
from utilities import utilities


class DonateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, min_length=3)
    coin = serializers.ChoiceField(choices=list(map(lambda x: x[1], Donate.COIN_CHOICES)))
    amount = serializers.FloatField()
    cost = serializers.ReadOnlyField()
    link = serializers.CharField(max_length=500, required=False, allow_blank=True)
    created = serializers.ReadOnlyField()

    def validate_amount(self, amount):
        if amount <= 0:
            raise exceptions.ValidationError(detail='Amount must be greater than zero!')
        return amount

    def to_representation(self, instance):
        instance.coin = instance.get_coin_display()
        instance.created = instance.created.strftime('%Y-%m-%d %H:%M')
        instance = super().to_representation(instance)
        if instance['cost'] <= 0:
            instance.pop('cost')
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        for item in Donate.COIN_CHOICES:
            if item[1] == data['coin']:
                data['coin'] = item[0]
        return data

    @transaction.atomic
    def create(self, validated_data):
        donate = Donate(**validated_data)
        donate.save()
        return donate
