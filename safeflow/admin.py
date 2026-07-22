from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from .models import Guardian, SafeTrip, TripEvent

class TripEventInline(StackedInline):
    model = TripEvent
    extra = 0
    classes = ("unfold-card",)

@admin.register(Guardian)
class GuardianAdmin(ModelAdmin):
    list_display = ("name", "user", "phone_number", "is_active")
    search_fields = ("name", "user__username")
    classes = ("unfold-card",)

@admin.register(SafeTrip)
class SafeTripAdmin(ModelAdmin):
    list_display = ("user", "status", "token", "created_at")
    list_filter = ("status",)
    inlines = [TripEventInline]
    readonly_fields = ("token", "created_at", "updated_at")
    classes = ("unfold-card",)

@admin.register(TripEvent)
class TripEventAdmin(ModelAdmin):
    list_display = ("trip", "stop", "description", "timestamp")
    classes = ("unfold-card",)