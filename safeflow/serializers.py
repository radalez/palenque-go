from rest_framework import serializers
from .models import Guardian, SafeTrip, TripEvent

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['id', 'name', 'phone_number', 'email', 'is_active']

class TripEventSerializer(serializers.ModelSerializer):
    stop_name = serializers.ReadOnlyField(source='stop.name')
    class Meta:
        model = TripEvent
        fields = ['id', 'stop_name', 'description', 'timestamp', 'latitude', 'longitude']

class SafeTripSerializer(serializers.ModelSerializer):
    events = TripEventSerializer(many=True, read_only=True)
    class Meta:
        model = SafeTrip
        fields = ['id', 'token', 'status', 'notify_on_checkpoints', 'share_gps_live', 'events', 'created_at']