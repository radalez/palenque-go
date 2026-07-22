from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer
from rest_framework import viewsets
from .models import Plan
from .serializers import PlanSerializer

import stripe
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken

# CONFIGURACIÓN STRIPE (Usa tu llave secreta del dashboard)
import os
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_replace_me")

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """Vista para registrar usuarios reales en la base de datos."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """Vista de login que devuelve los datos del usuario (ID, nombre) junto al token."""
    serializer_class = MyTokenObtainPairSerializer

class ChangePasswordView(APIView):
    """Vista para que un usuario autenticado cambie su contraseña."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': 'Debes enviar old_password y new_password'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': 'La contraseña actual es incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Contraseña actualizada con éxito'}, status=status.HTTP_200_OK)




class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista para que la App consulte los planes disponibles."""
    queryset = Plan.objects.all().order_by('precio_mensual')
    serializer_class = PlanSerializer
    permission_classes = [AllowAny] # O IsAuthenticated si prefieres


class CreateCheckoutSessionView(APIView):
    """Crea una sesión de Stripe Checkout para el plan seleccionado."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = Plan.objects.get(id=plan_id)

            # Construcción de la sesión de Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Suscripción: {plan.nombre}",
                            'description': f"Límite de {plan.limite_productos} productos",
                        },
                        'unit_amount': int(plan.precio_mensual * 100),  # Stripe procesa en centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:3000/plans?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:3000/plans',
                metadata={
                    'user_id': request.user.id,
                    'plan_id': plan.id
                }
            )
            return JsonResponse({'url': checkout_session.url})
        except Plan.DoesNotExist:
            return JsonResponse({'error': 'El plan no existe'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class CreateServicePaymentView(APIView):
    """Crea una sesión de Stripe para pagar un servicio individual."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        service_id = request.data.get('service_id')
        amount = request.data.get('amount')

        try:
            from services.models import Service
            service = Service.objects.get(id=service_id)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': service.nombre,
                            'description': f"Reserva de {service.nombre} en {service.tienda.nombre_comercial}",
                        },
                        'unit_amount': int(float(amount) * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                # URLS DE PRODUCCIÓN REALES
                success_url='https://palenquego6.netlify.app/dashboard?payment=success',
                cancel_url='https://palenquego6.netlify.app/explore',
                metadata={
                    'user_id': request.user.id,
                    'service_id': service.id,
                    'type': 'SERVICE_PAYMENT'
                }
            )
            return JsonResponse({'url': checkout_session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class GoogleLoginView(APIView):
    """Verifica el id_token de Google y devuelve tokens de sesión de Django."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({'error': 'Se requiere id_token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Usamos el Web Client ID
            CLIENT_ID = "922502878492-2ko3s5folq2q4nvgf9sae3mgnp5vlva5.apps.googleusercontent.com"
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)

            email = idinfo.get('email')
            name = idinfo.get('name', 'Usuario de Google')
            picture = idinfo.get('picture')

            if not email:
                return Response({'error': 'Google no proporcionó un email'}, status=status.HTTP_400_BAD_REQUEST)

            # Buscamos al usuario por correo, o lo creamos
            user, created = User.objects.get_or_create(email=email, defaults={
                'first_name': name,
                'username': email,
            })
            
            # Si el usuario ya existía pero no tenía nombre, se lo actualizamos
            if not created and user.first_name == '':
                user.first_name = name
                user.save()

            # Generamos los tokens de sesión de SimpleJWT
            refresh = RefreshToken.for_user(user)
            
            from marketing.models import Ambassador
            is_ambassador = Ambassador.objects.filter(usuario=user, esta_activo=True).exists()

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'name': user.first_name or user.username,
                    'email': user.email,
                    'telefono': getattr(user, 'telefono', ''),
                    'tipo': user.tipo_usuario,
                    'avatar': user.avatar.url if user.avatar else (picture if picture else "U"),
                    'is_ambassador': is_ambassador
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': 'Token inválido', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)