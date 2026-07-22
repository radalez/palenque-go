from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    MyTokenObtainPairView,
    PlanViewSet,
    CreateCheckoutSessionView,
    CreateServicePaymentView,
    ChangePasswordView
)

# Configuración del Router para la gestión dinámica de Planes
router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plans')

urlpatterns = [
    # Endpoints de Autenticación
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Endpoints de Planes y Membresías (Generados por el Router)
    path('', include(router.urls)),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='checkout_session'),
    path('pay-service/', CreateServicePaymentView.as_view(), name='pay_service'),
]