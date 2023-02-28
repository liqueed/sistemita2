"""Serializers de proveedores."""

# Imports
import json
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
from sistemita.core.models.proveedor import (
    FacturaDistribuidaProveedor,
    FacturaProveedor,
    FacturaProveedorImputada,
    Proveedor,
)
from sistemita.utils.commons import get_total_factura
from sistemita.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_MONEDA_INVALID,
    MESSAGE_NUMERO_EXISTS,
    MESSAGE_TIPO_DOC_IMPORT_INVALID,
    MESSAGE_TIPO_FACTURA_INVALID,
)
from sistemita.utils.validators import validate_is_number


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
        fields = [
            'id',
            'fecha',
            'numero',
            'proveedor',
            'tipo',
            'iva',
            'neto',
            'cobrado',
            'moneda',
            'total',
            'archivos',
            'monto_imputado',
            'total_sin_imputar',
        ]


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
    imp_neto_gravado = serializers.DecimalField(required=False, decimal_places=2, max_digits=12, allow_null=True)
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

    def validate_imp_neto_gravado(self, attr):
        """Valida el valor neto."""
        return attr or 0.0

    def validate(self, attrs):
        """Valida que el numero de factura no exita exista para el mismo emisor."""
        numero = attrs.get('punto_de_venta').zfill(5) + attrs.get('numero_desde').zfill(8)
        proveedor = self.context.get('proveedor', None)
        if FacturaProveedor.objects.filter(numero=numero, proveedor=proveedor).exists():
            raise serializers.ValidationError({'numero_desde': MESSAGE_NUMERO_EXISTS.format(numero, 'emisor')})
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


class FacturaProveedorImputadaModelSerializer(serializers.ModelSerializer):
    """Factura Imputada model Serializer."""

    fecha = serializers.DateField(required=True)
    facturas = FacturaProveedorSerializer(many=True, read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    proveedor_id = serializers.CharField(validators=[validate_is_number], write_only=True)
    facturas_list = serializers.ListField(child=serializers.DictField(), write_only=True)
    nota_de_credito = FacturaProveedorSerializer(read_only=True)
    nota_de_credito_id = serializers.CharField(validators=[validate_is_number], write_only=True)
    monto_facturas = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    monto_nota_de_credito = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    total_factura = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)

    class Meta:
        """Clase meta."""

        model = FacturaProveedorImputada
        fields = (
            'id',
            'fecha',
            'proveedor',
            'proveedor_id',
            'facturas',
            'facturas_list',
            'nota_de_credito',
            'nota_de_credito_id',
            'moneda',
            'monto_facturas',
            'monto_nota_de_credito',
            'total_factura',
        )
        read_only_fields = ('id', 'proveedor', 'facturas', 'nota_de_credito')

    def to_representation(self, instance):
        """Modifica el orden de las facturas imputadas."""
        rep = super().to_representation(instance)
        facturas = instance.facturas.all().order_by('facturas_imputacion')
        rep['facturas'] = FacturaProveedorSerializer(facturas, many=True).data
        return rep

    def validate_proveedor_id(self, data):
        """Valida datos de proveedor."""
        try:
            proveedor = Proveedor.objects.get(pk=data)
            self.context['proveedor'] = proveedor
            return proveedor
        except Proveedor.DoesNotExist as not_exist:
            raise serializers.ValidationError('El proveedor no existe.') from not_exist
        return data

    def validate_facturas_list(self, data):
        """
        Valida que las facturas sean de la misma moneda.
        Valida que las facturas sean del mismo proveedor.
        Valida que no haya dos facturas repetidas.
        """
        facturas = []
        monedas = []
        pks = []

        for row in data:
            try:
                proveedor = self.context.get('proveedor', None)
                factura = FacturaProveedor.objects.get(pk=row.get('factura'), proveedor=proveedor)
                facturas.append({'factura': factura, 'action': row.get('action')})
            except FacturaProveedor.DoesNotExist:
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
            proveedor = self.context.get('proveedor', None)
            return FacturaProveedor.objects.get(pk=data, proveedor=proveedor, tipo__startswith='NC')
        except FacturaProveedor.DoesNotExist as not_exist:
            raise serializers.ValidationError('La factura no existe.') from not_exist
        return data

    def validate(self, attrs):
        """
        Valida el monto de facturas.
        Valida el monto de nota de credito.
        Valida el total de factura.
        """
        total_factura = 0
        monto_facturas = 0

        for row in attrs.get('facturas_list'):
            if 'add' in row.get('action'):
                monto_facturas += row.get('factura').total_sin_imputar

            if 'update' in row.get('action'):
                monto_facturas += row.get('factura').total_sin_imputar

        # Valida el monto de facturas
        if attrs.get('monto_facturas') != monto_facturas:
            raise serializers.ValidationError({'monto_facturas': 'El monto de facturas no es correcto.'})

        # Validación del total de nota de credito
        if attrs.get('monto_nota_de_credito') != attrs.get('nota_de_credito_id').total_sin_imputar:
            raise serializers.ValidationError({'monto_nota_de_credito': 'El monto de nota de crédito no es correcto.'})

        # Valida el total factura
        total_factura = get_total_factura(monto_facturas, attrs.get('nota_de_credito_id').total_sin_imputar)
        if attrs.get('total_factura') != total_factura:
            raise serializers.ValidationError({'total_factura': 'El total de factura no es correcto.'})

        return attrs

    def create(self, validated_data):

        validated_data['proveedor'] = validated_data.pop('proveedor_id')
        validated_data['nota_de_credito'] = validated_data.pop('nota_de_credito_id')

        facturas = validated_data.pop('facturas_list')
        nota_de_credito = validated_data.get('nota_de_credito')
        total_nc = nota_de_credito.total
        instance = FacturaProveedorImputada.objects.create(**validated_data)

        for row in facturas:
            factura = row.get('factura')
            # Asignado facturas
            instance.facturas.add(factura)

            # Imputando costos
            if total_nc == 0:
                break
            factura_total = get_total_factura(factura.total, total_nc)
            factura.monto_imputado = factura.total if factura_total == 0 else total_nc
            total_nc -= factura.total if total_nc > factura.total else total_nc
            factura.total = factura_total
            factura.cobrado = not bool(factura.total)
            factura.save()

        nota_de_credito.monto_imputado = nota_de_credito.total - total_nc
        nota_de_credito.total = total_nc
        nota_de_credito.cobrado = not bool(nota_de_credito.total)
        nota_de_credito.save()

        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Edición de facturas imputadas."""
        facturas = validated_data.get('facturas_list')
        nota_de_credito = instance.nota_de_credito
        total_nc = nota_de_credito.total
        instance.monto_facturas = validated_data.get('monto_facturas')
        instance.total_factura = validated_data.get('total_factura')

        for row in facturas:
            factura = row.get('factura')
            action = row.get('action')
            if 'add' in action:
                instance.facturas.add(factura)
                if total_nc == 0:
                    break
                factura_total = get_total_factura(factura.total, total_nc)
                factura.monto_imputado = factura.total if factura_total == 0 else total_nc
                total_nc -= factura.total if total_nc > factura.total else total_nc
                factura.total = factura_total
                factura.cobrado = not bool(factura.total)
                factura.save()
            elif 'update' in action:
                replace_pk = json.loads(action.replace("'", "\""))['id']
                # Verifico si no son facturas iguales
                if factura.pk != replace_pk:
                    # Restablece los valores de la nota de credito
                    factura_repleace = FacturaProveedor.objects.get(pk=replace_pk)
                    nota_de_credito.total += factura_repleace.monto_imputado
                    nota_de_credito.monto_imputado -= factura_repleace.monto_imputado
                    nota_de_credito.save()
                    total_nc = nota_de_credito.total

                    # Restablece los valores de la factura a remplazar
                    factura_repleace.total += factura_repleace.monto_imputado
                    factura_repleace.monto_imputado = 0
                    factura_repleace.cobrado = False
                    factura_repleace.save()
                    instance.facturas.remove(factura_repleace)

                    # Imputa a la nueva factura
                    instance.facturas.add(factura)
                    factura_total = get_total_factura(factura.total, total_nc)
                    factura.monto_imputado = factura.total if factura_total == 0 else total_nc
                    total_nc -= factura.total if total_nc > factura.total else total_nc
                    factura.total = factura_total
                    factura.cobrado = not bool(factura.total)
                    factura.save()
            elif 'delete' in action:
                total_nc += factura.monto_imputado
                factura.total += factura.monto_imputado
                factura.cobrado = False
                factura.monto_imputado = 0
                factura.save()
                instance.facturas.remove(factura)

        nota_de_credito.monto_imputado = (nota_de_credito.total + nota_de_credito.monto_imputado) - total_nc
        nota_de_credito.total = total_nc
        nota_de_credito.cobrado = not bool(nota_de_credito.total)
        nota_de_credito.save()

        instance.save()
        return instance


class FacturaDistribuidaProveedorModelSerializer(serializers.ModelSerializer):
    """Serializador del modelo Factura Distribuida Proveedor."""

    proveedor = ProveedorSerializer()
    factura_proveedor = FacturaProveedorSerializer()

    class Meta:
        """Configuraciones del serializer."""

        model = FacturaDistribuidaProveedor
        fields = [
            'id',
            'proveedor',
            'detalle',
            'monto',
            'factura_proveedor',
        ]
