from rest_framework import serializers
from partners.models import Store
from .models import Category, Service, ServiceFeature, ServiceExtra, ServiceImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'nombre', 'icono']

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFeature
        fields = ['id', 'nombre']

class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExtra
        fields = ['id', 'nombre', 'precio_adicional']

class StoreSimpleSerializer(serializers.ModelSerializer):
    """Serializador básico de tienda para mostrar en la tarjeta del servicio."""
    class Meta:
        model = Store
        fields = ['id', 'nombre_comercial', 'logo', 'ubicacion_gps']

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ['id', 'imagen']

class ServiceSerializer(serializers.ModelSerializer):
    categoria = CategorySerializer(read_only=True)
    tienda = StoreSimpleSerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    extras = ExtraSerializer(many=True, read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'tienda', 'categoria', 'nombre', 'descripcion',
            'imagen_principal', 'precio_base', 'capacidad_min',
            'capacidad_max', 'permite_pool', 'features', 'extras', 'images', 'chatbot_script'
        ]