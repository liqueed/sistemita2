"""Modulo serializers."""

# Django REST Framework
from rest_framework import serializers

# Serializer
from core.serializers import ClienteSerializer

# Models
from core.models.cliente import Cliente
from accounting.models.cobranza import (
    Cobranza, CobranzaFactura, CobranzaFacturaPago
)


class CobranzaFacturaPagoSerializer(serializers.ModelSerializer):
    """Factura cobranza pago Serializer.

    Aparte de las propiedades del modelo, este serializer agrega el campo
    'data' para ser utilizado en la petición PUT. Este campo contiene si el objeto
    que lo contiene tiene que ser agregado, editado o eliminado.
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
    'data' para ser utilizado en la petición PUT. Este campo contiene si el objeto
    que lo contiene tiene que ser agregado, editado o eliminado.
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
    cliente = ClienteSerializer()
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    cobranza_facturas = CobranzaFacturaSerializer(many=True)

    class Meta:
        """Clase meta."""
        model = Cobranza
        fields = (
            'id', 'cliente', 'total',
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
            total = data['total']
            cobranza = Cobranza.objects.create(cliente=cliente, total=total)

            # Factura cobranza
            facturas = data['cobranza_facturas']
            for factura in facturas:
                cobranza_factura = CobranzaFactura.objects.create(
                    cobranza=cobranza,
                    factura=factura['factura'],
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
        # TODO: Agrega lógica para editar la cobranza
        try:
            instance.total = data['total']
            instance.save()
            return instance
        except Exception as error:
            raise serializers.ValidationError(error)
