"""Serializador de medio de pagos."""

# Django REST Framework
from rest_framework import serializers

# Sistemita
from sistemita.core.models.mediopago import MedioPago


class MedioPagoSerializer(serializers.ModelSerializer):
    """Serializer de MedioPago."""

    class Meta:
        """Configuraciones del serializer."""

        model = MedioPago
        fields = ('id', 'nombre')
