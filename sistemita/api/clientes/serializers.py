"""Serializadores de clientes."""

# Imports
from datetime import datetime
from re import match

# Django Rest Framework
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
from sistemita.core.models.cliente import Cliente, Factura
from sistemita.core.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_MONEDA_INVALID,
    MESSAGE_NUMERO_EXISTS,
    MESSAGE_TIPO_DOC_IMPORT_INVALID,
    MESSAGE_TIPO_FACTURA_INVALID,
)
from sistemita.core.utils.validators import validate_is_number


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer de Cliente."""

    provincia = ProvinciaSerializer(read_only=True)
    distrito = DistritoSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Cliente
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
            'tipo_envio_factura',
            'link_envio_factura',
            'correo_envio_factura',
        ]
        extra_kwargs = {
            'cuit': {'validators': []},
        }


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer de Factura."""

    archivos = ArchivoSerializer(many=True, read_only=True)
    cliente = ClienteSerializer(read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Factura
        fields = ['id', 'fecha', 'numero', 'cliente', 'tipo', 'moneda', 'neto', 'iva', 'cobrado', 'total', 'archivos']


class FacturaBeforeImportSerializer(serializers.Serializer):
    """Serializador para validar facturas a importar."""

    fecha = serializers.DateTimeField(input_formats=['%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'])

    tipo = serializers.CharField()
    numero = serializers.CharField(read_only=True)
    punto_de_venta = serializers.CharField(validators=[validate_is_number])
    numero_desde = serializers.CharField(validators=[validate_is_number])

    tipo_doc_receptor = serializers.CharField()
    nro_doc_receptor = serializers.IntegerField()
    denominacion_receptor = serializers.CharField()
    exists_receptor = serializers.BooleanField(read_only=True, default=False)

    moneda = serializers.CharField()
    imp_neto_gravado = serializers.DecimalField(required=False, decimal_places=2, max_digits=12, allow_null=True)
    imp_total = serializers.DecimalField(decimal_places=2, max_digits=12)

    def validate_tipo(self, attr):
        """Valida tipo de factura."""
        try:
            index = list(x[0] for x in TIPOS_FACTURA_IMPORT).index(attr)
        except ValueError as err:
            raise serializers.ValidationError(MESSAGE_TIPO_FACTURA_INVALID) from err
        return TIPOS_FACTURA_IMPORT[index][1]

    def validate_tipo_doc_receptor(self, attr):
        """Valida tipo de documento."""
        if attr not in TIPOS_DOC_IMPORT:
            raise serializers.ValidationError(MESSAGE_TIPO_DOC_IMPORT_INVALID)
        return attr

    def validate_nro_doc_receptor(self, attr):
        """Validate el cuit del cliente."""
        if not match(r'^[0-9]{11}$', str(attr)):
            raise serializers.ValidationError(MESSAGE_CUIT_INVALID)
        self.context['cliente'] = Cliente.objects.filter(cuit=attr).first()
        return attr

    def validate_moneda(self, attr):
        """Valida el tipo de moneda."""
        type_monedas = list(m[1] for m in MONEDAS)
        if attr not in type_monedas:
            raise serializers.ValidationError(MESSAGE_MONEDA_INVALID)
        return attr

    def validate_imp_neto_gravado(self, attr):
        """Valida el valor neto."""
        return attr or 0.0

    def validate(self, attrs):
        """Valida que el numero de factura no exita exista para el mismo receptor."""
        numero = attrs.get('punto_de_venta').zfill(5) + attrs.get('numero_desde').zfill(8)
        cliente = self.context.get('cliente', None)
        if Factura.objects.filter(numero=numero, cliente=cliente).exists():
            raise serializers.ValidationError({'numero_desde': MESSAGE_NUMERO_EXISTS.format(numero, 'receptor')})
        return attrs

    def to_representation(self, instance):
        """Modifica representación de los campos."""

        rep = super().to_representation(instance)
        rep['fecha'] = datetime.strptime(rep['fecha'][:19], '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y')
        rep['numero'] = rep['punto_de_venta'].zfill(5) + rep['numero_desde'].zfill(8)

        cliente = self.context.get('cliente', None)
        if cliente:
            rep['exists_receptor'] = True
            rep['denominacion_receptor'] = cliente.razon_social

        rep.pop('punto_de_venta')
        rep.pop('numero_desde')
        return rep


class FacturaImportSerializer(serializers.Serializer):
    """Serializador para validar facturas a importar."""

    fecha = serializers.DateTimeField(input_formats=['%d-%m-%Y'])
    numero = serializers.CharField()
    tipo = serializers.CharField()

    tipo_doc_receptor = serializers.CharField()
    nro_doc_receptor = serializers.CharField()
    denominacion_receptor = serializers.CharField()

    moneda = serializers.CharField()
    imp_neto_gravado = serializers.DecimalField(required=False, decimal_places=2, max_digits=12)
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
        Crea una factura asociandola a un cliente.
        Si el cliente no existe es creado.
        """
        cuit = validated_data.get('nro_doc_receptor')
        razon_social = validated_data.get('denominacion_receptor')
        cliente, _ = Cliente.objects.get_or_create(cuit=cuit, razon_social=razon_social)

        factura = Factura.objects.create(
            cliente=cliente,
            numero=validated_data.get('numero'),
            fecha=validated_data.get('fecha'),
            tipo=validated_data.get('tipo'),
            moneda=validated_data.get('moneda'),
            neto=validated_data.get('imp_neto_gravado'),
            total=validated_data.get('imp_total'),
        )

        return factura
