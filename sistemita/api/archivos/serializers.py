"""Serializadores del Archivos."""

# Django REST Framework
from rest_framework import serializers

# Modelo
from sistemita.core.models.archivo import Archivo


class ArchivoSerializer(serializers.ModelSerializer):
    """Serializer de Archivo."""

    class Meta:
        """Configuraciones del serializer."""

        model = Archivo
        fields = ('id', 'documento')
