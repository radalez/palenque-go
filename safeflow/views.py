from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Guardian, SafeTrip, TripEvent
from .serializers import GuardianSerializer, SafeTripSerializer
from .services import notify_guardians
from transport.models import Ticket, Stop


class SafeFlowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SafeTripSerializer

    def get_queryset(self):
        return SafeTrip.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def start_trip(self, request):
        """Activa el SafeFlow para un ticket específico"""
        ticket_id = request.data.get('ticket_id')
        notify_checkpoints = request.data.get('notify_checkpoints', False)

        try:
            ticket = Ticket.objects.get(id=ticket_id, user=request.user)
            trip, created = SafeTrip.objects.get_or_create(
                user=request.user,
                ticket=ticket,
                defaults={'notify_on_checkpoints': notify_checkpoints}
            )
            return Response(SafeTripSerializer(trip).data)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def scan_checkpoint(self, request, pk=None):
        """Simula el escaneo del QR de una parada o del bus"""
        trip = self.get_object()
        stop_id = request.data.get('stop_id')
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        try:
            stop = Stop.objects.get(id=stop_id)
            # Cambiamos el estado a EN RUTA si es el primer escaneo
            if trip.status == 'WAITING':
                trip.status = 'ON_ROUTE'
                trip.save()

            TripEvent.objects.create(
                trip=trip,
                stop=stop,
                description=f"Check-in en {stop.name}",
                latitude=lat,
                longitude=lng
            )
            return Response({"message": f"Check-in exitoso en {stop.name}"})
        except Stop.DoesNotExist:
            return Response({"error": "Parada no válida"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def scan_qr(self, request):
        """Endpoint para que el Frontend envíe el escaneo del QR y avise a los contactos"""
        token = request.data.get('token')
        
        try:
            trip = SafeTrip.objects.get(token=token)

            if trip.status == 'WAITING':
                trip.status = 'ON_ROUTE'
                trip.save()

                event_desc = "Abordaje confirmado en el autobús"
                TripEvent.objects.create(trip=trip, description=event_desc)

                # Disparar correos automáticos a los guardianes
                notify_guardians(trip, event_desc)

                return Response({"message": "Llegada confirmada y contactos notificados", "status": trip.status})
            else:
                return Response({"message": "El pasajero ya estaba a bordo", "status": trip.status})
                
        except SafeTrip.DoesNotExist:
            return Response({"error": "Código QR inválido o viaje no encontrado"}, status=status.HTTP_404_NOT_FOUND)


class PublicTrackerViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista para que la familia vea el viaje SIN LOGUEARSE"""
    permission_classes = [AllowAny]
    serializer_class = SafeTripSerializer
    lookup_field = 'token'
    queryset = SafeTrip.objects.all()


class GuardianViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GuardianSerializer

    def get_queryset(self):
        # Un usuario solo puede ver/editar sus propios guardianes
        return Guardian.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario logueado al guardián
        guardian = serializer.save(user=self.request.user)
        
        # Enviar correo de bienvenida con enlace a Telegram
        if guardian.email:
            from django.core.mail import send_mail
            from django.conf import settings
            bot_username = "PalenqueGoSeguridadBot"
            telegram_link = f"https://t.me/{bot_username}?start=guardian_{guardian.id}"
            
            subject = "¡Te han añadido como Contacto de Emergencia en Palenque Go!"
            message = (
                f"Hola {guardian.name},\n\n"
                f"{self.request.user.first_name or self.request.user.username} te ha agregado como su contacto de emergencia en Palenque Go.\n\n"
                f"Para recibir notificaciones en tiempo real sobre sus viajes directamente en Telegram, haz clic en el siguiente enlace y presiona 'Iniciar':\n\n"
                f"{telegram_link}\n\n"
                f"Si prefieres recibir solo correos, no es necesario que hagas nada más.\n\n"
                f"El equipo de Palenque Go"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [guardian.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"[SafeFlow] Error al enviar correo de bienvenida: {e}")

class TelegramWebhookViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Escucha los mensajes entrantes de Telegram"""
        try:
            data = request.data
            message = data.get('message', {})
            text = message.get('text', '')
            chat_id = message.get('chat', {}).get('id')
            
            if text.startswith('/start guardian_'):
                guardian_id = text.split('guardian_')[1]
                try:
                    guardian = Guardian.objects.get(id=guardian_id)
                    guardian.telegram_chat_id = str(chat_id)
                    guardian.save()
                    
                    # Enviar mensaje de confirmación
                    from .services import send_telegram_message
                    send_telegram_message(
                        chat_id, 
                        f"✅ ¡Hola {guardian.name}! Te has conectado exitosamente a las alertas de *SafeFlow*. A partir de ahora recibirás notificaciones en tiempo real de los viajes de {guardian.user.first_name or guardian.user.username} por este medio."
                    )
                except Guardian.DoesNotExist:
                    pass
            return Response({'status': 'ok'})
        except Exception as e:
            print(f"[Telegram Webhook ERROR]: {e}")
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)