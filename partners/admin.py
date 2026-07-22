from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Store

@admin.register(Store)
class StoreAdmin(ModelAdmin):
    """Gestión de la vitrina comercial del Aliado."""
    list_display = ("nombre_comercial", "aliado", "comision_pactada")
    search_fields = ("nombre_comercial", "aliado__username")