from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    # Traemos el nombre del usuario desde el modelo relacionado 'aliado'
    aliado_nombre = serializers.ReadOnlyField(source='aliado.username')

    class Meta:
        model = Store
        fields = [
            'id',
            'aliado_nombre',
            'nombre_comercial',
            'logo',
            'portada',
            'eslogan',
            'biografia',
            'ubicacion_gps'
            # 'creado_el' se eliminó porque no existe en el modelo Store
        ]