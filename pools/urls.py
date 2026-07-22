from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PoolViewSet

router = DefaultRouter()
router.register(r'', PoolViewSet, basename='pool')

urlpatterns = [
    path('', include(router.urls)),
]