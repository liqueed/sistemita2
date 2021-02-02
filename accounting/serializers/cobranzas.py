"""Serializers de los modelos Cobranza, CobranzaFactura y CobranzaFacturaPago."""

# Django REST Framework
from rest_framework import serializers

# Serialize
from core.serializers import ClienteSerializer

# Models
from core.models.cliente import Cliente, Factura
from accounting.models.cobranza import (
    Cobranza, CobranzaFactura, CobranzaFacturaPago
)


class CobranzaFacturaPagoSerializer(serializers.ModelSerializer):
    """Factura cobranza pago Serializer.

    Aparte de las propiedades del modelo, este serializer agrega el campo
    'data' para ser utilizado en la petición PUT.
    Este campo 'data' contiene informacion sobre si el objeto que lo contiene
    tiene que ser agregado, editado o eliminado.
    """

    data = serializers.DictField(required=False)

    class Meta:
        """Clase meta."""

        model = CobranzaFacturaPago
        fields = ('id', 'data', 'metodo', 'monto')
        read_only_fields = ('id',)


class CobranzaFacturaSerializer(serializers.ModelSerializer):
    """Factura cobranza Serializer.

    Aparte de las propiedades del modelo, este serializer agrega el campo
    'data' para ser utilizado en la petición PUT.
    Este campo 'data' contiene informacion sobre si el objeto que lo contiene
    tiene que ser agregado, editado o eliminado.
    """

    data = serializers.DictField(required=False)
    cobranza_factura_pagos = CobranzaFacturaPagoSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = CobranzaFactura
        fields = (
            'id', 'data',
            'factura', 'ganancias', 'ingresos_brutos', 'iva',
            'cobranza_factura_pagos'
        )
        read_only_fields = ('id',)


class CobranzaSerializer(serializers.ModelSerializer):
    """Cobranza Serializer."""

    fecha = serializers.DateField(required=True)
    cliente = ClienteSerializer()
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    cobranza_facturas = CobranzaFacturaSerializer(many=True)

    class Meta:
        """Clase meta."""

        model = Cobranza
        fields = (
            'id', 'fecha', 'cliente', 'total',
            'cobranza_facturas',
        )
        read_only_fields = ('id', 'cliente')

    def validate_cliente(self, data):
        """Valida datos de cliente."""
        try:
            cliente = Cliente.objects.get(cuit=data['cuit'])
            self.context['cliente'] = cliente
        except Cliente.DoesNotExist:
            raise serializers.ValidationError('Client does not exist.')
        return data

    def create(self, data):
        """Genera una cobranza con factura/s y su/s correspondiente/s pago/s."""
        try:
            # Factura
            cliente = self.context['cliente']
            fecha = data['fecha']
            total = data['total']
            cobranza = Cobranza.objects.create(fecha=fecha, cliente=cliente, total=total)

            # Factura cobranza
            facturas = data['cobranza_facturas']
            for factura in facturas:
                # La factura pasa a estar cobrada
                factura_entry = factura['factura']
                Factura.objects.filter(pk=factura_entry.id).update(cobrado=True)

                cobranza_factura = CobranzaFactura.objects.create(
                    cobranza=cobranza,
                    factura=factura_entry,
                    ganancias=factura['ganancias'],
                    ingresos_brutos=factura['ingresos_brutos'],
                    iva=factura['iva']
                )
                # Pagos
                pagos = factura['cobranza_factura_pagos']
                for pago in pagos:
                    CobranzaFacturaPago.objects.create(
                        cobranza_factura=cobranza_factura,
                        metodo=pago['metodo'],
                        monto=pago['monto']
                    )
            return cobranza
        except Exception as error:
            raise serializers.ValidationError(error)

    def update(self, instance, data):
        """Actualiza la intancia."""
        try:
            instance.fecha = data['fecha']
            instance.total = data['total']
            facturas = data['cobranza_facturas']

            # Recorro las facturas
            for factura in facturas:
                if factura['data']['action'] == 'add':
                    # Agrego factura cobranza

                    # La factura del cliente pasa a estar cobrada
                    factura_entry = factura['factura']
                    Factura.objects.filter(pk=factura_entry.id).update(cobrado=True)
                    cobranza_factura = CobranzaFactura.objects.create(
                        cobranza=instance,
                        factura=factura['factura'],
                        ganancias=factura['ganancias'],
                        ingresos_brutos=factura['ingresos_brutos'],
                        iva=factura['iva']
                    )

                    # pagos
                    pagos = factura['cobranza_factura_pagos']
                    for pago in pagos:
                        # Todos los pagos son nuevos al ser nueva la factura
                        CobranzaFacturaPago.objects.create(
                            cobranza_factura=cobranza_factura,
                            metodo=pago['metodo'],
                            monto=pago['monto']
                        )
                elif factura['data']['action'] == 'update':
                    # Actualizo factura de la cobranza
                    cobranza_factura = CobranzaFactura.objects.get(
                        pk=factura['data']['id']  # data contiene la pk de la factura cobranza
                    )

                    factura_entry = factura['factura']
                    if cobranza_factura.factura.id != factura_entry.id:
                        # Si la factura es diferente, la anterior pasa a estar no cobrada
                        Factura.objects.filter(pk=cobranza_factura.factura.id).update(
                            cobrado=False
                        )

                    # La factura actual del cliente pasa a estar cobrada
                    Factura.objects.filter(pk=factura_entry.id).update(cobrado=True)

                    CobranzaFactura.objects.filter(pk=factura['data']['id']).update(
                        factura=factura_entry,
                        ganancias=factura['ganancias'],
                        ingresos_brutos=factura['ingresos_brutos'],
                        iva=factura['iva']
                    )

                    # Pagos
                    pagos = factura['cobranza_factura_pagos']
                    for pago in pagos:
                        if pago['data']['action'] == 'update':
                            # Actualiza pago
                            CobranzaFacturaPago.objects.filter(pk=pago['data']['id']).update(
                                metodo=pago['metodo'],
                                monto=pago['monto']
                            )
                        elif pago['data']['action'] == 'add':
                            # Agrega Pago
                            CobranzaFacturaPago.objects.create(
                                cobranza_factura=cobranza_factura,
                                metodo=pago['metodo'],
                                monto=pago['monto']
                            )
                        elif pago['data']['action'] == 'delete':
                            # Elimina Pago
                            CobranzaFacturaPago.objects.get(pk=pago['data']['id']).delete()
                elif factura['data']['action'] == 'delete':
                    # Elimino la factura cobranza

                    # La facturas asociadas pasan a ser no cobradas
                    factura_entry = factura['factura']
                    Factura.objects.filter(pk=factura_entry.id).update(cobrado=False)

                    CobranzaFactura.objects.get(pk=factura['data']['id']).delete()

            instance.save()
            return instance
        except Exception as error:
            raise serializers.ValidationError(error)
