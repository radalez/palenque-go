from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from marketing.models import Ambassador
from .models import Plan
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('password', 'email', 'first_name', 'username')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está en uso.")
        return value

    def create(self, validated_data):
        email = validated_data.get('email', '')
        username = validated_data.get('username')
        
        if not username and email:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        elif not username:
            import uuid
            username = uuid.uuid4().hex[:10]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '')
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        # Convertimos 'data' a un diccionario genérico para que el IDE
        # deje de chillar por los tipos de datos
        data = dict(super().validate(attrs))
        from marketing.models import Ambassador
        is_ambassador = Ambassador.objects.filter(usuario=self.user, esta_activo=True).exists()
        data['user'] = {
            'id': self.user.id,
            'name': self.user.first_name or self.user.username,
            'email': self.user.email,
            'telefono': getattr(self.user, 'telefono', ''),
            'tipo': self.user.tipo_usuario,
            'avatar': self.user.avatar.url if self.user.avatar else "U",
            'is_ambassador': is_ambassador
        }

        return data


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'