from rest_framework import serializers
from .models import Pool, Ticket
from services.serializers import ServiceSerializer  # Asumiendo que tienes uno


class TicketSerializer(serializers.ModelSerializer):
    viajero_nombre = serializers.ReadOnlyField(source='viajero.username')

    class Meta:
        model = Ticket
        fields = ['id', 'viajero', 'viajero_nombre', 'estado_pago', 'codigo_qr', 'validado_el']


class PoolSerializer(serializers.ModelSerializer):
    servicio_detalle = ServiceSerializer(source='servicio', read_only=True)
    lider_nombre = serializers.ReadOnlyField(source='lider.username')
    miembros_count = serializers.SerializerMethodField()
    precio_persona = serializers.ReadOnlyField(source='precio_individual')

    class Meta:
        model = Pool
        fields = [
            'id', 'servicio', 'servicio_detalle', 'lider', 'lider_nombre',
            'estado', 'meta_personas', 'miembros_count', 'precio_total_servicio',
            'precio_persona', 'creado_el'
        ]

    def get_miembros_count(self, obj):
        return obj.tickets.count()