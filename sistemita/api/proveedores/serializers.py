"""Serializers de proveedores."""

# Imports
from datetime import datetime
from re import match

# Django REST Framework
from rest_framework import serializers

# Sistemita
from sistemita.api.archivos.serializers import ArchivoSerializer
from sistemita.api.entidades.serializers import (
    DistritoSerializer,
    LocalidadSerializer,
    ProvinciaSerializer,
)
from sistemita.core.constants import (
    MONEDAS,
    TIPOS_DOC_IMPORT,
    TIPOS_FACTURA,
    TIPOS_FACTURA_IMPORT,
)
from sistemita.core.models.proveedor import FacturaProveedor, Proveedor
from sistemita.core.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_MONEDA_INVALID,
    MESSAGE_NUMERO_EXISTS,
    MESSAGE_TIPO_DOC_IMPORT_INVALID,
    MESSAGE_TIPO_FACTURA_INVALID,
)
from sistemita.core.utils.validators import validate_is_number


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


class FacturaProveedorBeforeImportSerializer(serializers.Serializer):
    """Serializador para validar facturas a importar."""

    fecha = serializers.DateTimeField(input_formats=['%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'])

    tipo = serializers.CharField()
    numero = serializers.CharField(read_only=True)
    punto_de_venta = serializers.CharField(validators=[validate_is_number])
    numero_desde = serializers.CharField(validators=[validate_is_number])

    tipo_doc_emisor = serializers.CharField()
    nro_doc_emisor = serializers.IntegerField()
    denominacion_emisor = serializers.CharField()
    exists_emisor = serializers.BooleanField(read_only=True, default=False)

    moneda = serializers.CharField()
    imp_neto_gravado = serializers.DecimalField(decimal_places=2, max_digits=12)
    imp_total = serializers.DecimalField(decimal_places=2, max_digits=12)

    def validate_tipo(self, attr):
        """Valida tipo de factura."""
        try:
            index = list(x[0] for x in TIPOS_FACTURA_IMPORT).index(attr)
        except ValueError as err:
            raise serializers.ValidationError(MESSAGE_TIPO_FACTURA_INVALID) from err
        return TIPOS_FACTURA_IMPORT[index][1]

    def validate_tipo_doc_emisor(self, attr):
        """Valida tipo de documento."""
        if attr not in TIPOS_DOC_IMPORT:
            raise serializers.ValidationError(MESSAGE_TIPO_DOC_IMPORT_INVALID)
        return attr

    def validate_nro_doc_emisor(self, attr):
        """Validate el cuit del proveedor."""
        if not match(r'^[0-9]{11}$', str(attr)):
            raise serializers.ValidationError(MESSAGE_CUIT_INVALID)
        self.context['proveedor'] = Proveedor.objects.filter(cuit=attr).first()
        return attr

    def validate_moneda(self, attr):
        """Valida el tipo de moneda."""
        type_monedas = list(m[1] for m in MONEDAS)
        if attr not in type_monedas:
            raise serializers.ValidationError(MESSAGE_MONEDA_INVALID)
        return attr

    def validate(self, attrs):
        """Valida que el numero de factura no exita exista."""
        numero = attrs.get('punto_de_venta').zfill(5) + attrs.get('numero_desde').zfill(8)
        if FacturaProveedor.objects.filter(numero=numero).exists():
            raise serializers.ValidationError({'numero_desde': MESSAGE_NUMERO_EXISTS.format(numero)})
        return attrs

    def to_representation(self, instance):
        """Modifica representación de los campos."""

        rep = super().to_representation(instance)
        rep['fecha'] = datetime.strptime(rep['fecha'][:19], '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y')
        rep['numero'] = rep['punto_de_venta'].zfill(5) + rep['numero_desde'].zfill(8)

        proveedor = self.context.get('proveedor', None)
        if proveedor:
            rep['exists_emisor'] = True
            rep['denominacion_emisor'] = proveedor.razon_social

        rep.pop('punto_de_venta')
        rep.pop('numero_desde')
        return rep


class FacturaProveedorImportSerializer(serializers.Serializer):
    """Serializador para validar facturas a importar."""

    fecha = serializers.DateTimeField(input_formats=['%d-%m-%Y'])
    numero = serializers.CharField()
    tipo = serializers.CharField()

    tipo_doc_emisor = serializers.CharField()
    nro_doc_emisor = serializers.CharField()
    denominacion_emisor = serializers.CharField()

    moneda = serializers.CharField()
    imp_neto_gravado = serializers.DecimalField(decimal_places=2, max_digits=12)
    imp_total = serializers.DecimalField(decimal_places=2, max_digits=12)

    def validate_tipo(self, attr):
        """Validación de tipo de factura."""
        index = list(x[1] for x in TIPOS_FACTURA).index(attr)
        return TIPOS_FACTURA[index][0]

    def validate_moneda(self, attr):
        """Validación de tipo de factura."""
        index = list(x[1] for x in MONEDAS).index(attr)
        return MONEDAS[index][0]

    def create(self, validated_data):
        """
        Crea una factura asociandola a un proveedor.
        Si el proveedor no existe es creado.
        """
        cuit = validated_data.get('nro_doc_emisor')
        razon_social = validated_data.get('denominacion_emisor')
        proveedor, _ = Proveedor.objects.get_or_create(cuit=cuit, razon_social=razon_social)

        factura = FacturaProveedor.objects.create(
            proveedor=proveedor,
            numero=validated_data.get('numero'),
            fecha=validated_data.get('fecha'),
            tipo=validated_data.get('tipo'),
            moneda=validated_data.get('moneda'),
            neto=validated_data.get('imp_neto_gravado'),
            total=validated_data.get('imp_total'),
        )

        return factura
