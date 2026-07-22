from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Service, UserSwipe
from .serializers import CategorySerializer, ServiceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar las categorías (Hotelería, Surf, etc.)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """API para el catálogo con filtros de búsqueda."""
    queryset = Service.objects.filter(activo=True)
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtros exactos y por rango
    filterset_fields = {
        'categoria': ['exact'],
        'precio_base': ['gte', 'lte'],  # gte = Mayor o igual, lte = Menor o igual
        'permite_pool': ['exact'],
    }

    # Búsqueda por texto (nombre y descripción)
    search_fields = ['nombre', 'descripcion']

    # Ordenamiento (por precio o nombre)
    ordering_fields = ['precio_base', 'nombre']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def swipe(self, request, pk=None):
        """Registrar el swipe de un usuario (es_like: bool)."""
        servicio = self.get_object()
        es_like = request.data.get('es_like', False)
        
        # Guardamos el swipe o lo actualizamos
        swipe, created = UserSwipe.objects.update_or_create(
            usuario=request.user,
            servicio=servicio,
            defaults={'es_like': es_like}
        )
        return Response({'status': 'swipe registered', 'es_like': swipe.es_like})
