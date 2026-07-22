from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, Plan

@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ("nombre", "precio_mensual", "limite_productos", "permite_rutas")
    search_fields = ("nombre",)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Panel de usuario personalizado con soporte para roles y wallet[cite: 256, 261]."""
    list_display = ("username", "email", "tipo_usuario", "plan", "wallet_balance")
    list_filter = ("tipo_usuario", "plan")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Información Palenque", {"fields": ("tipo_usuario", "telefono", "avatar", "wallet_balance", "plan")}),
    )