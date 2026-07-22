from rest_framework import serializers
from .models import Route, Stop, Unit

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'order', 'latitude', 'longitude', 'minutes_from_start']

class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    unit_name = serializers.ReadOnlyField(source='unit.name')
    unit_id = serializers.ReadOnlyField(source='unit.id')
    unit_lat = serializers.ReadOnlyField(source='unit.current_lat')
    unit_lng = serializers.ReadOnlyField(source='unit.current_lng')

    user_has_ticket = serializers.SerializerMethodField()

    def get_user_has_ticket(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Pasajero con boleto activo
        if obj.ticket_set.filter(user=request.user, is_used=False).exists():
            return True
        # Chofer asignado a la unidad de esta ruta
        if obj.unit and obj.unit.driver == request.user:
            return True
        return False

    class Meta:
        model = Route
        fields = [
            'id', 'name', 'unit_id', 'unit_name', 'unit_lat', 'unit_lng',
            'price_one_way', 'price_round_trip', 'is_active', 'stops',
            'user_has_ticket'
        ]

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'license_plate', 'capacity', 'current_lat', 'current_lng', 'last_location_update', 'driver']