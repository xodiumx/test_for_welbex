from django.shortcuts import get_object_or_404

from rest_framework.serializers import (
    ImageField, ModelSerializer, PrimaryKeyRelatedField, ReadOnlyField,
    Serializer, SerializerMethodField, CharField, IntegerField
)

from .exceptions import WeightException, SameValueException
from .models import (
    Cargo, Location, MAX_LENGTH_OF_CARGO_DESCRIPTION,
    MAX_WEIGHT_OF_CARGO, MIN_WEIGHT_OF_CARGO, CARGO_ZIP_MAX_LENGTH 
)


class CargoInfoSerializer(ModelSerializer):

    class Meta:
        model = Cargo
        fields = ('pick_up', 'delivery_to') # TODO: counts aoto


class CargoCreateSerializer(ModelSerializer):

    class Meta:
        model = Cargo
        fields = ('pick_up', 'delivery_to', 'weight', 'description')

    def validate(self, data):
        """
        Достаем значения 'pick_up' и 'delivery' 
        из не десериализованной data
        """
        data['pick_up'] = self.initial_data.get('pick_up')
        data['delivery_to'] = self.initial_data.get('delivery_to')
        
        if data.get('pick_up') == data.get('delivery_to'):
            raise SameValueException(
                {'detail': 'Одинаковое местоположение груза и доставки'})
        return data
    
    def create(self, validated_data):
        """
        Для создания, проверям есть ли локации с такими индексами в базе.
        """
        validated_data['pick_up'] = get_object_or_404(
            Location, zip_index=self.validated_data.get('pick_up'))
        validated_data['delivery_to'] = get_object_or_404(
            Location, zip_index=self.validated_data.get('delivery_to'))
        return Cargo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Для обновления груза, берем новое значение из validated_data, 
        если его нет берем старое.
        """
        instance.weight = validated_data.get('weight', instance.weight)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """
        Для ответа меняем id на zip_index
        """
        data = super().to_representation(instance)
        data['pick_up'] = str(instance.pick_up)
        data['delivery_to'] = str(instance.delivery_to)
        return data


class CarSerializer(ModelSerializer):
    ...