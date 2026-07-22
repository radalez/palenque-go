from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Pool, Ticket


class TicketInline(TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ("codigo_qr", "validado_el")


@admin.register(Pool)
class PoolAdmin(ModelAdmin):
    """Gestión del motor financiero de grupos."""
    list_display = ("servicio", "lider", "estado", "meta_personas", "precio_individual_display", "precio_total_servicio")
    list_filter = ("estado", "creado_el")
    inlines = [TicketInline]

    # Campo calculado para ver el precio individual en el listado
    def precio_individual_display(self, obj):
        return f"${obj.precio_individual:.2f}"

    precio_individual_display.short_description = "Precio Individual"


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    """Control de validación de entradas por QR."""
    list_display = ("codigo_qr", "viajero", "pool", "estado_pago", "validado_el")
    list_filter = ("estado_pago", "validado_el")
    search_fields = ("codigo_qr", "viajero__username")