from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Service, ServiceFeature, ServiceExtra, ServiceImage, UserSwipe

class ServiceImageInline(TabularInline):
    model = ServiceImage
    extra = 1

class ServiceFeatureInline(TabularInline):
    model = ServiceFeature
    extra = 1

class ServiceExtraInline(TabularInline):
    model = ServiceExtra
    extra = 1

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    """Gestión del catálogo de servicios para la API de Next.js."""
    list_display = ("nombre", "tienda", "precio_base", "permite_pool", "activo")
    list_filter = ("permite_pool", "activo", "categoria")
    search_fields = ("nombre", "tienda__nombre_comercial")
    inlines = [ServiceImageInline, ServiceFeatureInline, ServiceExtraInline]


@admin.register(UserSwipe)
class UserSwipeAdmin(ModelAdmin):
    """Registro de swipes (likes/nopes) de usuarios sobre servicios."""
    list_display = ("usuario", "servicio", "es_like", "fecha")
    list_filter = ("es_like", "servicio__categoria", "servicio")
    search_fields = ("usuario__username", "usuario__email", "servicio__nombre")
    ordering = ("-fecha",)
    readonly_fields = ("usuario", "servicio", "es_like", "fecha")

    def has_add_permission(self, request):
        return False  # Los swipes los genera la app, no el admin

    def has_delete_permission(self, request, obj=None):
        return True