from rest_framework import viewsets
from .models import Store
from .serializers import StoreSerializer

class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """API para listar y ver detalles de las tiendas aliadas."""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer