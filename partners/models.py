from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
class Store(models.Model):
    """La vitrina o tienda personalizada de cada Aliado."""
    aliado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores', verbose_name=_("Aliado"))
    nombre_comercial = models.CharField(_("Nombre Comercial"), max_length=200)
    logo = models.ImageField(_("Logo de la Tienda"), upload_to='stores/logos/', blank=True, null=True)
    portada = models.ImageField(_("Imagen de Portada"), upload_to='stores/covers/', blank=True, null=True)
    eslogan = models.CharField(_("Eslogan"), max_length=255, blank=True)
    biografia = models.TextField(_("Historia/Bio"), help_text=_("Historia y alma del negocio"))
    ubicacion_gps = models.CharField(_("Ubicación GPS"), max_length=100, help_text="Lat, Lng")
    comision_pactada = models.DecimalField(_("Comisión Pactada (%)"), max_digits=5, decimal_places=2, default=15.00)

    class Meta:
        verbose_name = _("Tienda")
        verbose_name_plural = _("Tiendas")

    def __str__(self):
        return self.nombre_comercial

