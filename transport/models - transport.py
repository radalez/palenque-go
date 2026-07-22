from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Route(models.Model):
    """Define trayectos físicos como la 'Ruta del Sol'."""
    nombre = models.CharField(_("Nombre de la Ruta"), max_length=100)
    path_svg = models.TextField(_("Trazo SVG"), help_text=_("Coordenadas para dibujo en mapa"))
    color_hex = models.CharField(_("Color Hexadecimal"), max_length=7, default="#FF5733")
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Creador"))

    class Meta:
        verbose_name = _("Ruta")
        verbose_name_plural = _("Rutas")

    def __str__(self):
        return self.nombre

class Stop(models.Model):
    """Puntos de control y paradas de seguridad en la ruta"""
    ruta = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    nombre = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    orden = models.PositiveIntegerField()

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} ({self.ruta.nombre})"

class Unit(models.Model):
    """Buses físicos que operan la red[cite: 275]."""
    ESTADOS = (('EN_RUTA', 'En Ruta'), ('TALLER', 'En Taller'), ('ESPERA', 'En Espera'))
    placa = models.CharField(max_length=20, unique=True)
    chofer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ESPERA')

    def __str__(self):
        return self.placa