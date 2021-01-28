"""Serializers de la app 'core'."""

# Django REST Framework
from rest_framework import serializers

# Models
from core.models.archivo import Archivo
from core.models.cliente import Cliente, Factura
from core.models.entidad import Provincia, Distrito, Localidad
from core.models.mediopago import MedioPago
from core.models.proveedor import Proveedor, FacturaProveedor


class ProvinciaSerializer(serializers.ModelSerializer):
    """Serializer de Provincia."""

    class Meta:
        """Configuraciones del serializer."""

        model = Provincia
        fields = ['id', 'nombre']


class DistritoSerializer(serializers.ModelSerializer):
    """Serializer de Distrito."""

    class Meta:
        """Configuraciones del serializer."""

        model = Distrito
        fields = ['id', 'nombre', 'provincia']


class LocalidadSerializer(serializers.ModelSerializer):
    """Serializer de Localidad."""

    class Meta:
        """Configuraciones del serializer."""

        model = Localidad
        fields = ['id', 'nombre', 'distrito']


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer de Cliente."""

    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Cliente
        fields = [
            'id', 'razon_social', 'cuit', 'correo', 'telefono',
            'calle', 'numero', 'piso', 'dpto',
            'provincia', 'distrito', 'localidad',
            'tipo_envio_factura', 'link_envio_factura', 'correo_envio_factura'
        ]
        extra_kwargs = {
            'cuit': {'validators': []},
        }


class ArchivoSerializer(serializers.ModelSerializer):
    """Serializer de Archivo."""

    class Meta:
        """Configuraciones del serializer."""

        model = Archivo
        fields = ['id', 'documento']


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer de Factura."""

    archivos = ArchivoSerializer(many=True, read_only=True)
    cliente = ClienteSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Factura
        fields = ['id', 'cliente', 'cobrado', 'fecha', 'total', 'archivos']


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer de Proveedor."""

    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Proveedor
        fields = [
            'id', 'razon_social', 'cuit', 'correo', 'telefono',
            'calle', 'numero', 'piso', 'dpto',
            'provincia', 'distrito', 'localidad',
            'cbu'
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
        fields = ['id', 'proveedor', 'cobrado', 'fecha', 'total', 'archivos']


class MedioPagoSerializer(serializers.ModelSerializer):
    """Serializer de MedioPago."""

    class Meta:
        """Configuraciones del serializer."""

        model = MedioPago
        fields = ['id', 'nombre']
