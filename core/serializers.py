from rest_framework import serializers

from core.models import Distrito, Localidad, Cliente, Provincia


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
