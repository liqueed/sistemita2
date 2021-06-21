"""Serializadores de entidades."""

# Django REST Framework
from rest_framework import serializers

# Modelos
from sistemita.core.models.entidad import Distrito, Localidad, Provincia


class ProvinciaSerializer(serializers.ModelSerializer):
    """Serializer de Provincia."""

    class Meta:
        """Configuraciones del serializer."""

        model = Provincia
        fields = ('id', 'nombre')


class DistritoSerializer(serializers.ModelSerializer):
    """Serializer de Distrito."""

    class Meta:
        """Configuraciones del serializer."""

        model = Distrito
        fields = ('id', 'nombre', 'provincia')


class LocalidadSerializer(serializers.ModelSerializer):
    """Serializer de Localidad."""

    class Meta:
        """Configuraciones del serializer."""

        model = Localidad
        fields = ('id', 'nombre', 'distrito')
