"""
URL configuration for palenque_flow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
"""


from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from accounts.views import RegisterView, MyTokenObtainPairView, PlanViewSet, CreateCheckoutSessionView, CreateServicePaymentView, ChangePasswordView, GoogleLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('palenque-go/', TemplateView.as_view(template_name='palenque-go.html'), name='palenque_go'),
    path('admin/', admin.site.urls),
    path('api/v1/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/v1/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/v1/auth/plans/', PlanViewSet.as_view({'get': 'list'}), name='plans-list'),
    path('api/v1/auth/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='checkout_session'),
    path('api/v1/auth/pay-service/', CreateServicePaymentView.as_view(), name='pay_service'),
    path('api/v1/', include('services.urls')),
    path('api/v1/stores/', include('partners.urls')),
    path('api/v1/transport/', include('transport.urls')),
    path('api/v1/pools/', include('pools.urls')),
    path('api/v1/marketing/', include('marketing.urls')),
    path('api/v1/safeflow/', include('safeflow.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = "Palenque Flow"
admin.site.site_title = "Palenque Admin"
admin.site.index_title = "Bienvenidos al Ecosistema Palenque"