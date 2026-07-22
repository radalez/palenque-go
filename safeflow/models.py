import uuid
# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.conf import settings
from transport.models import Ticket, Stop


class Guardian(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guardians")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, help_text="Formato internacional: +503...", blank=True, null=True)
    email = models.EmailField(blank=True, null=True, help_text="Correo electrónico para notificaciones")
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID de chat de Telegram")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Guardián de {self.user.username})"


class SafeTrip(models.Model):
    STATUS_CHOICES = (
        ('WAITING', 'Esperando Abordaje'),
        ('ON_ROUTE', 'En Ruta'),
        ('ARRIVED', 'Llegada Segura'),
        ('ALERT', '¡ALERTA!'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="safe_flow")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')

    # Configuración del usuario
    notify_on_checkpoints = models.BooleanField(default=False)
    share_gps_live = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SafeFlow: {self.user.username} - {self.status}"


class TripEvent(models.Model):
    trip = models.ForeignKey(SafeTrip, on_delete=models.CASCADE, related_name="events")
    stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.trip.user.username} en {self.description}"