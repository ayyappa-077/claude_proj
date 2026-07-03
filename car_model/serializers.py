from rest_framework import serializers
from .models import CarModel, CarListing


class CarModelSerializer(serializers.ModelSerializer):
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)

    class Meta:
        model = CarModel
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class CarListingSerializer(serializers.ModelSerializer):
    car = CarModelSerializer(read_only=True)
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(),
        source='car',
        write_only=True,
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CarListing
        fields = '__all__'
        read_only_fields = ('id', 'listed_date')