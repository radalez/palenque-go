from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Plan(models.Model):
    """Define los niveles de membresía y sus libertades."""
    nombre = models.CharField(_("Nombre del Plan"), max_length=50)
    precio_mensual = models.DecimalField(_("Precio Mensual"), max_digits=10, decimal_places=2, default=0.00)
    limite_productos = models.IntegerField(_("Límite de Productos"), default=5)
    comision_plataforma = models.PositiveIntegerField(_("Comisión Plataforma (%)"), default=15)
    permite_rutas = models.BooleanField(_("Permite Crear Rutas"), default=False)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Planes")

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    """Extensión del usuario para manejar roles y economía circular[cite: 248, 256]."""
    TIPOS_USUARIO = (
        ('VIAJERO', 'Viajero'),
        ('CHOFER', 'Chofer'),
        ('ALIADO', 'Aliado/Dueño'),
        ('EMBAJADOR', 'Embajador'),
        ('ADMIN', 'Administrador'),
    )
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='VIAJERO')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"