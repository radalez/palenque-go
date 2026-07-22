from django.db import models
from django.conf import settings
from partners.models import Store

class Category(models.Model):
    """Categorías del marketplace: Hotelería, Surf, Café, etc."""
    nombre = models.CharField(max_length=100)
    icono = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.nombre

class Service(models.Model):
    """Producto principal: Habitación, Tour de Café, Clase de Surf."""
    tienda = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='services')
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen_principal = models.ImageField(upload_to='services/main/', blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    capacidad_min = models.PositiveIntegerField(default=1)
    capacidad_max = models.PositiveIntegerField(default=10)
    permite_pool = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    chatbot_script = models.TextField(blank=True, null=True, help_text="Script JS del chatbot de ventas para este servicio")

    def __str__(self):
        return f"{self.nombre} - {self.tienda.nombre_comercial}"

class ServiceFeature(models.Model):
    """Características INCLUIDAS en el servicio (Check verde en la UI)."""
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"Incluye: {self.nombre}"

class ServiceExtra(models.Model):
    """Variables o agregados: Desayuno, Alquiler de equipo, Guía privado."""
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='extras')
    nombre = models.CharField(max_length=100)
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"+ {self.nombre} (${self.precio_adicional})"

class ServiceImage(models.Model):
    """Galería de imágenes adicionales para el Swipe (Tinder-style)."""
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    imagen = models.ImageField(upload_to='services/gallery/')

    def __str__(self):
        return f"Imagen extra de {self.servicio.nombre}"

class UserSwipe(models.Model):
    """Registro de la decisión del usuario (Like/Favorito o Rechazo)."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes')
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='swipes')
    es_like = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'servicio')

    def __str__(self):
        return f"{self.usuario.username} - {self.servicio.nombre} - {'Like' if self.es_like else 'Rechazo'}"