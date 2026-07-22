import uuid
from django.db import models
from django.conf import settings
from partners.models import Service
from django.utils.translation import gettext_lazy as _

class Pool(models.Model):
    """El motor de compra grupal y división de costos."""
    ESTADOS = (
        ('ABIERTO', _('Abierto (Buscando gente)')),
        ('LLENO', _('Lleno (Listo para pagar)')),
        ('PAGADO', _('Pagado (Confirmado)')),
        ('FINALIZADO', _('Finalizado (Servicio prestado)')),
    )
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='pools', verbose_name=_("Servicio"))
    lider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='led_pools', verbose_name=_("Líder del Grupo"))
    estado = models.CharField(_("Estado"), max_length=15, choices=ESTADOS, default='ABIERTO')
    meta_personas = models.PositiveIntegerField(_("Meta de Personas"), help_text=_("Cuántos faltan para cerrar el grupo"))
    precio_total_servicio = models.DecimalField(_("Precio Total"), max_digits=10, decimal_places=2)
    monto_comision_lider = models.DecimalField(_("Comisión para el Líder"), max_digits=10, decimal_places=2, default=0.00)
    creado_el = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)

    class Meta:
        verbose_name = _("Pool (Grupo)")
        verbose_name_plural = _("Pools (Grupos)")

    @property
    def precio_individual(self):
        if self.meta_personas > 0:
            return self.precio_total_servicio / self.meta_personas
        return 0

    def __str__(self):
        return f"Grupo: {self.servicio.nombre} (Líder: {self.lider.username})"

class Ticket(models.Model):
    """La inscripción individual y el QR de validación."""
    ESTADOS_PAGO = (('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'))
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='tickets')
    viajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estado_pago = models.CharField(max_length=10, choices=ESTADOS_PAGO, default='PENDIENTE')
    codigo_qr = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    validado_el = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.codigo_qr[:8]} - {self.viajero.username}"