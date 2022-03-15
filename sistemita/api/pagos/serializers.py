"""Serializers de los modelos Pago, PagoFactura y PagoFacturaPago."""

# Django REST Framework
from rest_framework import serializers

# Sistemita
from sistemita.accounting.models.pago import Pago, PagoFactura, PagoFacturaPago
from sistemita.api.proveedores.serializers import ProveedorSerializer
from sistemita.core.models.proveedor import FacturaProveedor, Proveedor


class PagoFacturaPagoSerializer(serializers.ModelSerializer):
    """Pago de Factura pago Serializer.

    Aparte de las propiedades del modelo, este serializer agrega el campo
    'data' para ser utilizado en la petición PUT.
    Este campo 'data' contiene informacion sobre si el objeto que lo contiene
    tiene que ser agregado, editado o eliminado.
    """

    data = serializers.DictField(required=False)

    class Meta:
        """Clase meta."""

        model = PagoFacturaPago
        fields = ('id', 'data', 'metodo', 'monto')
        read_only_fields = ('id',)

    def validate(self, attrs):
        """Valida que el metodo no sea nulo y hay un monto."""
        if attrs.get('monto') and not attrs.get('metodo'):
            raise serializers.ValidationError({'metodo': 'Este campo no puede ser nulo.'})
        return attrs


class PagoFacturaSerializer(serializers.ModelSerializer):
    """Factura pago Serializer.

    Aparte de las propiedades del modelo, este serializer agrega el campo
    'data' para ser utilizado en la petición PUT.
    Este campo 'data' contiene informacion sobre si el objeto que lo contiene
    tiene que ser agregado, editado o eliminado.
    """

    data = serializers.DictField(required=False)
    pago_factura_pagos = PagoFacturaPagoSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = PagoFactura
        fields = ('id', 'data', 'factura', 'ganancias', 'ingresos_brutos', 'iva', 'suss', 'pago_factura_pagos')
        read_only_fields = ('id',)


class PagoModelSerializer(serializers.ModelSerializer):
    """Pago Model Serializer."""

    fecha = serializers.DateField(required=True)
    proveedor = ProveedorSerializer()
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    pagado = serializers.BooleanField(default=False)
    pago_facturas = PagoFacturaSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = Pago
        fields = (
            'id',
            'fecha',
            'proveedor',
            'moneda',
            'total',
            'pagado',
            'pago_facturas',
        )
        read_only_fields = ('id', 'proveedor')


class CreateUpdatePagoModelSerializer(serializers.ModelSerializer):
    """Pago Model Serializer."""

    fecha = serializers.DateField(required=True)
    proveedor = serializers.CharField(max_length=11)
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    pagado = serializers.BooleanField(default=False)
    pago_facturas = PagoFacturaSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = Pago
        fields = (
            'id',
            'fecha',
            'proveedor',
            'moneda',
            'total',
            'pagado',
            'pago_facturas',
        )
        read_only_fields = ('id', 'proveedor')

    def validate_proveedor(self, attr):
        """Valida datos de proveedor."""
        try:
            proveedor = Proveedor.objects.get(cuit=attr)
        except Proveedor.DoesNotExist as not_exist:
            raise serializers.ValidationError('El proveedor no existe.') from not_exist
        return proveedor

    def validate_pago_facturas(self, data):
        """Valida que las facturas sean de la misma moneda y que no haya dos facturas repetidas."""
        monedas = []
        pks = []
        for row in data:
            if row.get('data', False):
                if row['data']['action'] in ['add', 'update']:
                    monedas.append(row.get('factura').moneda)
                    pks.append(row.get('factura').pk)
            else:
                monedas.append(row.get('factura').moneda)
                pks.append(row.get('factura').pk)

        if len(monedas) > 1 and len(set(monedas)) > 1:
            raise serializers.ValidationError('Las facturas deben ser de la misma monedas.')

        if len(pks) > 1:
            if len(pks) != len(set(pks)):
                raise serializers.ValidationError('Hay facturas repetidas.')

        return data

    def create(self, validated_data):
        """Genera un pago con factura/s y su/s correspondiente/s pago/s."""
        try:
            # Factura
            fecha = validated_data['fecha']
            proveedor = validated_data['proveedor']
            moneda = validated_data['moneda']
            total = validated_data['total']
            pagado = validated_data['pagado']
            pago = Pago.objects.create(fecha=fecha, proveedor=proveedor, moneda=moneda, total=total, pagado=pagado)

            # Factura pago
            facturas = validated_data['pago_facturas']
            for factura in facturas:
                # La factura pasa a estar cobrada
                factura_entry = factura['factura']
                FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=True)

                pago_factura = PagoFactura.objects.create(
                    pago=pago,
                    factura=factura_entry,
                    ganancias=factura['ganancias'],
                    ingresos_brutos=factura['ingresos_brutos'],
                    iva=factura['iva'],
                    suss=factura['suss'],
                )
                # Pagos
                pagos = factura['pago_factura_pagos']
                for row in pagos:
                    PagoFacturaPago.objects.create(pago_factura=pago_factura, metodo=row['metodo'], monto=row['monto'])
        except Exception as error:
            raise serializers.ValidationError(error)
        return pago

    def update(self, instance, validated_data):
        """Actualiza la instancia."""
        try:
            instance.fecha = validated_data['fecha']
            instance.total = validated_data['total']
            instance.pagado = validated_data['pagado']
            facturas = validated_data['pago_facturas']

            # Recorro las facturas
            for factura in facturas:
                if factura['data']['action'] == 'add':
                    # Agrego factura pago

                    # La factura del proveedor pasa a estar cobrada
                    factura_entry = factura['factura']
                    FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=True)

                    pago_factura = PagoFactura.objects.create(
                        pago=instance,
                        factura=factura['factura'],
                        ganancias=factura['ganancias'],
                        ingresos_brutos=factura['ingresos_brutos'],
                        iva=factura['iva'],
                        suss=factura['suss'],
                    )

                    # pagos
                    pagos = factura['pago_factura_pagos']
                    for row in pagos:
                        # Todos los pagos son nuevos al ser nueva la factura
                        PagoFacturaPago.objects.create(
                            pago_factura=pago_factura, metodo=row['metodo'], monto=row['monto']
                        )
                elif factura['data']['action'] == 'update':
                    # Actualizo factura del pago
                    pago_factura = PagoFactura.objects.get(
                        pk=factura['data']['id']  # data contiene la pk de la factura de pago
                    )

                    factura_entry = factura['factura']
                    if pago_factura.factura.id != factura_entry.id:
                        # Si la factura es diferente, la anterior pasa a estar no cobrada
                        FacturaProveedor.objects.filter(pk=pago_factura.factura.id).update(cobrado=False)

                    # La factura actual del proveedor pasa a estar cobrada
                    FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=True)

                    PagoFactura.objects.filter(pk=factura['data']['id']).update(
                        factura=factura_entry,
                        ganancias=factura['ganancias'],
                        ingresos_brutos=factura['ingresos_brutos'],
                        iva=factura['iva'],
                        suss=factura['suss'],
                    )

                    # Pagos
                    pagos = factura['pago_factura_pagos']
                    for row in pagos:
                        if row['data']['action'] == 'update':
                            # Actualiza pago
                            PagoFacturaPago.objects.filter(pk=row['data']['id']).update(
                                metodo=row['metodo'], monto=row['monto']
                            )
                        elif row['data']['action'] == 'add':
                            # Agrega Pago
                            PagoFacturaPago.objects.create(
                                pago_factura=pago_factura, metodo=row['metodo'], monto=row['monto']
                            )
                        elif row['data']['action'] == 'delete':
                            # Elimina Pago
                            PagoFacturaPago.objects.get(pk=row['data']['id']).delete()
                elif factura['data']['action'] == 'delete':
                    # Elimino la factura de pago

                    # La facturas asociadas pasan a ser no cobradas
                    factura_entry = factura['factura']
                    FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=False)

                    PagoFactura.objects.get(pk=factura['data']['id']).delete()

            instance.save()
            return instance
        except Exception as error:
            raise serializers.ValidationError(error)
