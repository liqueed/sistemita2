"""Serializadores de clientes."""

# Imports
import json
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
from sistemita.core.models.cliente import Cliente, Factura, FacturaImputada
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


class FacturaImputadaModelSerializer(serializers.ModelSerializer):
    """Factura Imputada model Serializer."""

    fecha = serializers.DateField(required=True)
    facturas = FacturaSerializer(many=True, read_only=True)
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.CharField(validators=[validate_is_number], write_only=True)
    facturas_list = serializers.ListField(child=serializers.DictField(), write_only=True)
    nota_de_credito = FacturaSerializer(read_only=True)
    nota_de_credito_id = serializers.CharField(validators=[validate_is_number], write_only=True)
    monto_facturas = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    monto_nota_de_credito = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    total_factura = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)

    class Meta:
        """Clase meta."""

        model = FacturaImputada
        fields = (
            'id',
            'fecha',
            'cliente',
            'cliente_id',
            'facturas',
            'facturas_list',
            'nota_de_credito',
            'nota_de_credito_id',
            'moneda',
            'monto_facturas',
            'monto_nota_de_credito',
            'total_factura',
        )
        read_only_fields = ('id', 'cliente', 'facturas', 'nota_de_credito')

    def validate_cliente_id(self, data):
        """Valida datos de cliente."""
        try:
            cliente = Cliente.objects.get(pk=data)
            self.context['cliente'] = cliente
            return cliente
        except Cliente.DoesNotExist as not_exist:
            raise serializers.ValidationError('Client does not exist.') from not_exist
        return data

    def validate_facturas_list(self, data):
        """Valida que las facturas sean de la misma moneda y que no haya dos facturas repetidas."""
        facturas = []
        monedas = []
        pks = []

        for row in data:
            try:
                factura = Factura.objects.get(pk=row.get('factura'))
                facturas.append({'factura': factura, 'action': row.get('action')})
            except Factura.DoesNotExist:
                raise serializers.ValidationError('La factura no existe.')

            if row.get('action') in ['add', 'update']:
                monedas.append(factura.moneda)
                pks.append(factura.pk)

        if len(monedas) > 1 and len(set(monedas)) > 1:
            raise serializers.ValidationError('Las facturas deben ser de la misma monedas.')

        if len(pks) > 1:
            if len(pks) != len(set(pks)):
                raise serializers.ValidationError('Hay facturas repetidas.')

        return facturas

    def validate_nota_de_credito_id(self, data):
        """Valida la nota de crédito."""
        try:
            cliente = self.context.get('cliente', None)
            return Factura.objects.get(pk=data, cliente=cliente, tipo__startswith='NC')
        except Factura.DoesNotExist as not_exist:
            raise serializers.ValidationError('La factura no existe.') from not_exist
        return data

    def create(self, validated_data):

        validated_data['cliente'] = validated_data.pop('cliente_id')
        validated_data['nota_de_credito'] = validated_data.pop('nota_de_credito_id')

        facturas = validated_data.pop('facturas_list')
        nota_de_credito = validated_data.get('nota_de_credito')
        total_nc = nota_de_credito.total
        instance = FacturaImputada.objects.create(**validated_data)

        for row in facturas:
            factura = row.get('factura')
            # Asignado facturas
            instance.facturas.add(factura)

            # Imputando costos
            if total_nc == 0:
                break
            if total_nc == factura.total:
                factura.monto_imputado = total_nc
                total_nc -= factura.total
                factura.cobrado = True
                factura.total = 0
            elif total_nc > factura.total:
                total_nc -= factura.total
                factura.monto_imputado = factura.total
                factura.cobrado = True
                factura.total = 0
            elif total_nc < factura.total:
                factura.monto_imputado = total_nc
                factura.total -= total_nc
                total_nc = 0

            factura.save()

        nota_de_credito.monto_imputado = nota_de_credito.total - total_nc
        nota_de_credito.total = total_nc
        if nota_de_credito.total == 0:
            nota_de_credito.cobrado = True
        nota_de_credito.save()

        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Edición de facturas imputadas."""
        facturas = validated_data.get('facturas_list')
        nota_de_credito = instance.nota_de_credito
        total_nc = nota_de_credito.total

        for row in facturas:
            factura = row.get('factura')
            action = row.get('action')
            if 'add' in action:
                instance.facturas.add(factura)
                if total_nc == 0:
                    break
                if total_nc == factura.total:
                    factura.monto_imputado = total_nc
                    total_nc -= factura.total
                    factura.cobrado = True
                    factura.total = 0
                elif total_nc > factura.total:
                    total_nc -= factura.total
                    factura.monto_imputado = factura.total
                    factura.cobrado = True
                    factura.total = 0
                elif total_nc < factura.total:
                    factura.monto_imputado = total_nc
                    factura.total -= total_nc
                    total_nc = 0
                factura.save()
            elif 'update' in action:
                replace_pk = json.loads(action.replace("'", "\""))['id']
                # Verifico si no son facturas iguales
                if factura.pk != replace_pk:
                    # Restablece los valores de la factura remplaza
                    factura_repleace = Factura.objects.get(pk=replace_pk)
                    nota_de_credito.total += factura_repleace.monto_imputado
                    nota_de_credito.monto_imputado -= factura_repleace.monto_imputado
                    nota_de_credito.save()
                    total_nc = nota_de_credito.total

                    factura_repleace.total += factura_repleace.monto_imputado
                    factura_repleace.monto_imputado = 0
                    factura_repleace.cobrado = False
                    factura_repleace.save()
                    instance.facturas.remove(factura_repleace)

                    # Imputa a la nueva factura
                    instance.facturas.add(factura)
                    if total_nc == factura.total:
                        factura.monto_imputado = total_nc
                        total_nc -= factura.total
                        factura.cobrado = True
                        factura.total = 0
                    elif total_nc > factura.total:
                        total_nc -= factura.total
                        factura.monto_imputado = factura.total
                        factura.cobrado = True
                        factura.total = 0
                    elif total_nc < factura.total:
                        factura.monto_imputado = total_nc
                        factura.total -= total_nc
                        total_nc = 0
                    factura.save()
            elif 'delete' in action:
                total_nc += factura.monto_imputado
                factura.total += factura.monto_imputado
                factura.cobrado = False
                factura.monto_imputado = 0
                factura.save()
                instance.facturas.remove(factura)

        nota_de_credito.monto_imputado = nota_de_credito.total - total_nc
        nota_de_credito.total = total_nc
        if nota_de_credito.total == 0:
            nota_de_credito.cobrado = True
        nota_de_credito.save()

        instance.save()
        return instance
