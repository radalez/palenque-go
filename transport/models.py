from django.db import models
from django.conf import settings
# Importamos el modelo de Servicios para hacer el puente
from services.models import Service  # Asegúrate que el nombre de la app sea 'services'


class Unit(models.Model):
    name = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)
    capacity = models.IntegerField(default=10)

    # NUEVO: Enlace directo al usuario que maneja esta unidad
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'tipo_usuario': 'CHOFER'}
    )

    # --- GPS DINÁMICO (Para el rastreo real) ---
    current_lat = models.FloatField(null=True, blank=True, help_text="Latitud actual del GPS")
    current_lng = models.FloatField(null=True, blank=True, help_text="Longitud actual del GPS")
    last_location_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.license_plate})"


class Route(models.Model):
    name = models.CharField(max_length=200)
    # El 'chef' que maneja el bus
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    # Precios diferenciados según tu UI
    price_one_way = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_round_trip = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Control de visibilidad en la App
    is_active = models.BooleanField(default=True)

    # El PUENTE: Conexión con los servicios de los Partners
    included_services = models.ManyToManyField(Service, blank=True, related_name="included_in_routes")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Stop(models.Model):
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Para el rastreador: "Llega en X min"
    minutes_from_start = models.IntegerField(help_text="Minutos estimados desde el punto de inicio")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.route.name}"


class Ticket(models.Model):
    # Tipos de boleto
    TICKET_TYPES = (
        ('ONE_WAY', 'Solo Ida'),
        ('ROUND_TRIP', 'Ida y Vuelta'),
    )

    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transport_tickets'
    )
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Boleto {self.id} - {self.user.username}"