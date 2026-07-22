from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pool, Ticket
from .serializers import PoolSerializer


class PoolViewSet(viewsets.ModelViewSet):
    queryset = Pool.objects.all().order_by('-creado_el')
    serializer_class = PoolSerializer

    # Acción para unirse a un pool
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        pool = self.get_object()
        if pool.tickets.count() >= pool.meta_personas:
            return Response({'error': 'Pool lleno'}, status=status.HTTP_400_BAD_REQUEST)

        ticket, created = Ticket.objects.get_or_create(
            pool=pool,
            viajero=request.user,
            defaults={'estado_pago': 'PENDIENTE'}
        )

        if not created:
            return Response({'message': 'Ya eres parte de este pool'}, status=status.HTTP_200_OK)
        # En views.py
        return Response({'message': 'Te has unido con éxito'}, status=status.HTTP_201_CREATED)