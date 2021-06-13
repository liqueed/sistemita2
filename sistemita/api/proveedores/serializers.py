"""Serializers de proveedores."""

# Django REST Framework
from rest_framework import serializers

# Sistemita
from sistemita.api.archivos.serializers import ArchivoSerializer
from sistemita.api.entidades.serializers import (
    DistritoSerializer,
    LocalidadSerializer,
    ProvinciaSerializer,
)
from sistemita.core.models.proveedor import FacturaProveedor, Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer de Proveedor."""

    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Proveedor
        fields = [
            'id',
            'razon_social',
            'cuit',
            'correo',
            'telefono',
            'calle',
            'numero',
            'piso',
            'dpto',
            'provincia',
            'distrito',
            'localidad',
            'cbu',
        ]
        extra_kwargs = {
            'cuit': {'validators': []},
        }


class FacturaProveedorSerializer(serializers.ModelSerializer):
    """Serializer de FacturaProveedor."""

    archivos = ArchivoSerializer(many=True, read_only=True)
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = FacturaProveedor
        fields = ['id', 'fecha', 'proveedor', 'tipo', 'iva', 'neto', 'cobrado', 'total', 'archivos']
