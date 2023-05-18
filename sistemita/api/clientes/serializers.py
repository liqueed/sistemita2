"""Serializadores de clientes."""

# Imports
import json
from datetime import datetime
from decimal import Decimal
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
from sistemita.api.proveedores.serializers import (
    FacturaDistribuidaProveedorModelSerializer,
)
from sistemita.core.constants import (
    MONEDAS,
    TIPOS_DOC_IMPORT,
    TIPOS_FACTURA,
    TIPOS_FACTURA_IMPORT,
)
from sistemita.core.models.cliente import (
    Cliente,
    Contrato,
    Factura,
    FacturaDistribuida,
    FacturaImpuesto,
    FacturaImputada,
)
from sistemita.core.models.proveedor import (
    FacturaDistribuidaProveedor,
    Proveedor,
)
from sistemita.utils.commons import get_total_factura
from sistemita.utils.emails import send_notification_factura_distribuida
from sistemita.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_MONEDA_INVALID,
    MESSAGE_NUMERO_EXISTS,
    MESSAGE_TIPO_DOC_IMPORT_INVALID,
    MESSAGE_TIPO_FACTURA_INVALID,
)
from sistemita.utils.validators import validate_is_number


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
        # Quito validadores para utilizar en cobranzas/pagos
        # Este serializer no se usa para crear clientes, por lo cual los validadores no tienen importacia
        extra_kwargs = {
            'cuit': {'validators': []},
            'correo': {'validators': []},
        }


class FacturaImpuestoModelSerializer(serializers.ModelSerializer):
    """Serializer del model Factura impuesto."""

    class Meta:
        """Configuraciones del serializer."""

        model = FacturaImpuesto
        fields = [
            'id',
            'detalle',
            'monto',
        ]


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer de Factura."""

    archivos = ArchivoSerializer(many=True, read_only=True)
    cliente = ClienteSerializer(read_only=True)
    impuestos = FacturaImpuestoModelSerializer(many=True, read_only=True)

    class Meta:
        """Configuraciones del serializer."""

        model = Factura
        fields = [
            'id',
            'fecha',
            'numero',
            'cliente',
            'tipo',
            'moneda',
            'neto',
            'iva',
            'cobrado',
            'total',
            'archivos',
            'monto_imputado',
            'monto_a_distribuir',
            'factura_distribuida',
            'impuestos',
        ]


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

    def to_representation(self, instance):
        """Modifica el orden de las facturas imputadas."""
        rep = super().to_representation(instance)
        facturas = instance.facturas.all().order_by('facturas_imputacion')
        rep['facturas'] = FacturaSerializer(facturas, many=True).data
        return rep

    def validate_cliente_id(self, data):
        """Valida datos de cliente."""
        try:
            cliente = Cliente.objects.get(pk=data)
            self.context['cliente'] = cliente
            return cliente
        except Cliente.DoesNotExist as not_exist:
            raise serializers.ValidationError('El cliente no existe.') from not_exist
        return data

    def validate_facturas_list(self, data):
        """
        Valida que las facturas sean de la misma moneda.
        Valida que las facturas sean del mismo cliente.
        Valida que no haya dos facturas repetidas.
        """
        facturas = []
        monedas = []
        pks = []

        for row in data:
            try:
                cliente = self.context.get('cliente', None)
                factura = Factura.objects.get(pk=row.get('factura'), cliente=cliente)
                facturas.append({'factura': factura, 'action': row.get('action')})
            except Factura.DoesNotExist:
                raise serializers.ValidationError('La factura o el cliente no existe.')

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
            raise serializers.ValidationError('La nota de crédito no existe.') from not_exist
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
                    factura_repleace = Factura.objects.get(pk=replace_pk)
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


class FacturaDistribuidaModelSerializer(serializers.ModelSerializer):
    """Serializar del modelo Factura distribuida"""

    factura = FacturaSerializer()
    factura_distribuida_proveedores = FacturaDistribuidaProveedorModelSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = FacturaDistribuida
        fields = ('id', 'factura', 'monto_distribuido', 'factura_distribuida_proveedores')
        read_only_fields = ('id', 'factura', 'monto_distribuido', 'factura_distribuida_proveedores')


class FacturaDistribuidaSerializer(serializers.Serializer):
    """Serializador de distribución de factura cliente."""

    factura_distribuida_id = serializers.CharField()
    distribucion_list = serializers.ListField(child=serializers.DictField())

    def validate_factura_distribuida_id(self, data):
        """Valida datos de proveedor."""
        try:
            factura_distribuida = FacturaDistribuida.objects.get(pk=data)
            self.context['factura_distribuida'] = factura_distribuida
        except FacturaDistribuida.DoesNotExist as not_exist:
            raise serializers.ValidationError('La factura distribuida no existe.') from not_exist
        return factura_distribuida

    def validate_distribucion_list(self, data):
        """
        Valida que los proveedores sean válidos.
        """
        distribucion = []
        montos = 0
        factura_distribuida = self.context.get('factura_distribuida', None)

        for row in data:
            try:
                proveedor = Proveedor.objects.get(pk=row.get('id'))
                data = row.get('data')
                distribucion.append(
                    {'proveedor': proveedor, 'detalle': row.get('detalle'), 'monto': row.get('monto'), 'data': data}
                )
                if data.get('action') in ['add', 'update']:
                    montos += float(row.get('monto'))
            except Proveedor.DoesNotExist:
                raise serializers.ValidationError('El proveedor no existe.')

        if round(Decimal(montos), 2) > factura_distribuida.factura.monto_a_distribuir:
            raise serializers.ValidationError('Los montos no pueden superar al total de la factura.')

        return distribucion

    def create(self, validated_data):
        """Crea instancia"""
        facturadistribuida = validated_data.get('factura_distribuida_id')
        distribucion_list = validated_data.get('distribucion_list')
        monto_distribuido = 0
        proveedores_list = []

        for item in distribucion_list:
            monto = item.get('monto')
            monto_distribuido += float(monto)
            proveedor = item.get('proveedor')
            detalle = item.get('detalle', '')
            FacturaDistribuidaProveedor.objects.create(
                factura_distribucion=facturadistribuida, detalle=detalle, proveedor=proveedor, monto=monto
            )
            send_notification_factura_distribuida(proveedor, facturadistribuida)
            proveedores_list.append({'id': item.get('proveedor').pk})

        if round(Decimal(monto_distribuido), 2) == facturadistribuida.factura.monto_a_distribuir:
            facturadistribuida.distribuida = True

        facturadistribuida.monto_distribuido = monto_distribuido
        facturadistribuida.save()

        return {'factura_distribuida_id': facturadistribuida.pk, 'distribucion_list': proveedores_list}

    def update(self, instance, validated_data):
        """Edita la instancia."""
        facturadistribuida = validated_data.get('factura_distribuida_id')
        distribucion_list = validated_data.get('distribucion_list')
        monto_distribuido = 0
        proveedores_list = []

        for item in distribucion_list:
            detalle = item.get('detalle', '')
            monto = item.get('monto')
            data = item.get('data')
            if data.get('action') == 'add':
                monto_distribuido += float(monto)
                proveedor = item.get('proveedor')
                FacturaDistribuidaProveedor.objects.create(
                    factura_distribucion=facturadistribuida,
                    proveedor=proveedor,
                    detalle=detalle,
                    monto=monto,
                )
                send_notification_factura_distribuida(proveedor, facturadistribuida)
                proveedores_list.append({'id': item.get('proveedor').pk})
            elif data.get('action') == 'update':
                proveedor = item.get('proveedor')
                monto_distribuido += float(monto)
                FacturaDistribuidaProveedor.objects.filter(id=data.get('id')).update(
                    proveedor=proveedor, monto=monto, detalle=detalle
                )
            elif data.get('action') == 'delete':
                FacturaDistribuidaProveedor.objects.filter(id=data.get('id')).delete()

        facturadistribuida.monto_distribuido = monto_distribuido
        if round(Decimal(monto_distribuido), 2) == facturadistribuida.factura.monto_a_distribuir:
            facturadistribuida.distribuida = True
        else:
            facturadistribuida.distribuida = False
        facturadistribuida.save()

        return {'factura_distribuida_id': facturadistribuida.pk, 'distribucion_list': proveedores_list}


class FacturaDistribuidaSendNotificationSerializer(serializers.Serializer):
    """Serializadorr para enviar notificaciones de factura distribuida a un proveedor."""

    proveedor_id = serializers.CharField()
    factura_distribuida_id = serializers.CharField()

    def validate_proveedor_id(self, data):
        """Valida proveedor."""
        try:
            proveedor = Proveedor.objects.get(pk=data)
        except Proveedor.DoesNotExist:
            raise serializers.ValidationError('El proveedor no existe.')
        return proveedor

    def validate_factura_distribuida_id(self, data):
        """Valida la factura distribuida."""
        try:
            facturadistribuida = FacturaDistribuida.objects.get(pk=data)
        except FacturaDistribuida.DoesNotExist:
            raise serializers.ValidationError('La factura distribuida no existe.')
        return facturadistribuida

    def create(self, validated_data):
        """Envía notificación."""
        proveedor = validated_data.get('proveedor_id')
        facturadistribuida = validated_data.get('factura_distribuida_id')
        send_notification_factura_distribuida(proveedor, facturadistribuida)
        return True


class ContratoModelSerializer(serializers.ModelSerializer):
    """Serializador del modelo Contrato"""

    class Meta:
        """Clase meta."""

        model = Contrato
        fields = ('id', 'categoria')
        read_only_fields = ('id', 'categoria')
