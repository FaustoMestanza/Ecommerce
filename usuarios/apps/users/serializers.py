"""Lógica de serialización para la app `users`.

Los serializers convierten instancias de modelos a JSON y validan datos
entrantes para crear o actualizar. Este serializer expone un subconjunto
mínimo de los campos del usuario; información sensible como `password` se
omite intencionadamente.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()  # resuelve al modelo de usuario personalizado definido arriba


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para objetos User.

    Los campos incluidos son los comúnmente requeridos por aplicaciones cliente.
    Agrega más campos aquí a medida que crezcan los requerimientos.
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Este campo es obligatorio."})

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
