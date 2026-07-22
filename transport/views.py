from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Route, Unit, Ticket
from .serializers import RouteSerializer, UnitSerializer

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # ADMIN/Staff ve TODAS (activas e inactivas), activas primero
        if user.is_staff or user.is_superuser or getattr(user, 'tipo_usuario', '') == 'ADMIN':
            return Route.objects.all().order_by('-is_active', 'name')
        
        # CHOFER: ve todas las rutas activas (el serializer marca la suya)
        if getattr(user, 'tipo_usuario', '') == 'CHOFER':
            return Route.objects.filter(is_active=True).order_by('-is_active', 'name')
        
        # PASAJERO: todas las rutas activas. El serializer marca cuál tiene su boleto.
        return Route.objects.filter(is_active=True).order_by('-is_active', 'name')

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my-unit')
    def my_unit(self, request):
        """Devuelve la unidad asignada al chofer que hace la petición."""
        try:
            unit = Unit.objects.get(driver=request.user)
            return Response({
                'id': unit.id,
                'name': unit.name,
                'license_plate': unit.license_plate,
                'current_lat': unit.current_lat,
                'current_lng': unit.current_lng,
            })
        except Unit.DoesNotExist:
            return Response({'error': 'No tienes ningún vehículo asignado.'}, status=status.HTTP_404_NOT_FOUND)
        except Unit.MultipleObjectsReturned:
            # Si tiene varios, devolvemos el primero
            unit = Unit.objects.filter(driver=request.user).first()
            return Response({
                'id': unit.id,
                'name': unit.name,
                'license_plate': unit.license_plate,
                'current_lat': unit.current_lat,
                'current_lng': unit.current_lng,
            })

    @action(detail=True, methods=['patch'])
    def update_location(self, request, pk=None):
        import math
        unit = self.get_object()
        
        # Seguridad: solo el chofer asignado puede mover su bus
        if unit.driver != request.user:
            return Response(
                {'error': 'No tienes permiso para actualizar el GPS de este vehículo.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            lat = float(request.data.get('lat'))
            lng = float(request.data.get('lng'))
        except (TypeError, ValueError):
            return Response({'error': 'Coordenadas inválidas'}, status=status.HTTP_400_BAD_REQUEST)
            
        unit.current_lat = lat
        unit.current_lng = lng
        unit.save()
        
        is_trip_finished = False
        
        # Lógica de detección de paradas en vivo (Auto-Check-in)
        if unit.route:
            from safeflow.models import SafeTrip, TripEvent
            from safeflow.services import notify_guardians
            
            # Solo analizamos viajes activos para esta ruta
            active_trips = SafeTrip.objects.filter(ticket__route=unit.route, status__in=['WAITING', 'ON_ROUTE'])
            
            if active_trips.exists():
                stops = unit.route.stops.all().order_by('order')
                
                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371e3
                    p1 = math.radians(lat1)
                    p2 = math.radians(lat2)
                    dp = math.radians(lat2 - lat1)
                    dl = math.radians(lon2 - lon1)
                    a = math.sin(dp/2) * math.sin(dp/2) + math.cos(p1) * math.cos(p2) * math.sin(dl/2) * math.sin(dl/2)
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    return R * c
                
                for stop in stops:
                    dist = haversine(lat, lng, stop.latitude, stop.longitude)
                    # Si el bus está a 50 metros o menos de la parada
                    if dist <= 50:
                        for trip in active_trips:
                            # Verificamos si ya habíamos registrado esta parada para este viaje
                            if not TripEvent.objects.filter(trip=trip, stop=stop).exists():
                                if trip.status == 'WAITING':
                                    trip.status = 'ON_ROUTE'
                                    trip.save()
                                
                                is_last_stop = (stop == stops.last())
                                
                                if is_last_stop:
                                    trip.status = 'ARRIVED'
                                    trip.save()
                                    event_desc = f"🏁 ¡Viaje Concluido! El pasajero ha llegado a su destino en: {stop.name}."
                                    is_trip_finished = True
                                else:
                                    event_desc = f"El bus de la ruta '{unit.route.name}' acaba de pasar por la parada: {stop.name}"
                                
                                TripEvent.objects.create(
                                    trip=trip, stop=stop, description=event_desc,
                                    latitude=lat, longitude=lng
                                )
                                notify_guardians(trip, event_desc)
                                
        return Response({
            'status': 'ubicación actualizada',
            'is_trip_finished': is_trip_finished
        })

    @action(detail=True, methods=['post'])
    def pass_stop(self, request, pk=None):
        """El chofer marca que ha pasado por una parada"""
        unit = self.get_object()
        
        if unit.driver != request.user:
            return Response(
                {'error': 'No tienes permiso.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        stop_id = request.data.get('stop_id')
        try:
            from .models import Stop
            stop = Stop.objects.get(id=stop_id, route=unit.route)
        except Stop.DoesNotExist:
            return Response({'error': 'Parada inválida'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Buscar viajes activos en esta ruta
        from safeflow.models import SafeTrip, TripEvent
        from safeflow.services import notify_guardians
        
        active_trips = SafeTrip.objects.filter(
            ticket__route=unit.route, 
            status__in=['WAITING', 'ON_ROUTE']
        )
        
        notified_count = 0
        for trip in active_trips:
            # Si estaba esperando, ahora está en ruta
            if trip.status == 'WAITING':
                trip.status = 'ON_ROUTE'
                trip.save()
                
            event_desc = f"El bus de la ruta '{unit.route.name}' acaba de pasar por la parada: {stop.name}"
            
            TripEvent.objects.create(
                trip=trip,
                stop=stop,
                description=event_desc,
                latitude=unit.current_lat,
                longitude=unit.current_lng
            )
            
            # Enviar correo a contactos
            notify_guardians(trip, event_desc)
            notified_count += 1
            
        return Response({
            'status': 'Parada marcada', 
            'notified_passengers': notified_count
        })