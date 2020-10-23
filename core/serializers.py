from rest_framework import serializers

from core.models import Archivo, Cliente, Distrito, Factura, FacturaProveedor, Localidad, \
    Proveedor, Provincia


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['id', 'nombre']


class DistritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distrito
        fields = ['id', 'nombre', 'provincia']


class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ['id', 'nombre', 'distrito']


class ClienteSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'razon_social', 'cuit', 'correo', 'telefono', 'calle', 'numero', 'piso', 'dpto', 'provincia',
                  'distrito', 'localidad', 'tipo_envio_factura', 'link_envio_factura', 'correo_envio_factura']


class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = ['id', 'documento']


class FacturaSerializer(serializers.ModelSerializer):
    archivos = ArchivoSerializer(many=True, read_only=True)

    class Meta:
        model = Factura
        fields = ['id', 'archivos']


class ProveedorSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        model = Proveedor
        fields = ['id', 'razon_social', 'cuit', 'correo', 'telefono', 'calle', 'numero', 'piso', 'dpto', 'provincia',
                  'distrito', 'localidad', 'cbu']


class FacturaProveedorSerializer(serializers.ModelSerializer):
    archivos = ArchivoSerializer(many=True, read_only=True)

    class Meta:
        model = FacturaProveedor
        fields = ['id', 'archivos']
