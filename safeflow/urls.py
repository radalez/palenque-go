from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SafeFlowViewSet, PublicTrackerViewSet, GuardianViewSet, TelegramWebhookViewSet

router = DefaultRouter()
router.register(r'trips', SafeFlowViewSet, basename='safetrip')
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'public-track', PublicTrackerViewSet, basename='public-track')
router.register(r'telegram', TelegramWebhookViewSet, basename='telegram')

urlpatterns = [
    path('', include(router.urls)),
]