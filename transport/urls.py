from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, UnitViewSet


router = DefaultRouter()
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'units', UnitViewSet, basename='unit')

urlpatterns = [
    path('', include(router.urls)),
]