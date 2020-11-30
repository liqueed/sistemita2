"""Modulo serializers."""

# Django REST Framework
from rest_framework import serializers

# Serializer
from core.serializers import ClienteSerializer, FacturaSerializer

# Models
from core.models.cliente import Cliente, Factura
from core.models.mediopago import MedioPago
from accounting.models.cobranza import (
    Cobranza, CobranzaFactura, CobranzaFacturaPago
)


class CobranzaFacturaPagoSerializer(serializers.ModelSerializer):
    """Cobr"""
    class Meta:
        model = CobranzaFacturaPago
        fields = ('metodo', 'monto')


class CobranzaFacturaSerializer(serializers.ModelSerializer):
    cobranza_factura_pagos = CobranzaFacturaPagoSerializer(many=True)

    class Meta:
        model = CobranzaFactura
        fields = (
            'factura',
            'ganancias', 'ingresos_brutos', 'iva',
            'cobranza_factura_pagos'
        )


class CobranzaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    cobranza_facturas = CobranzaFacturaSerializer(many=True)

    class Meta:
        model = Cobranza
        fields = ('id', 'cliente', 'cobranza_facturas', 'total')
        read_only_fields = ('id',)


class AddCobranzaSerializer(serializers.ModelSerializer):
    cliente = serializers.IntegerField(required=True)
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    cobranza_facturas = CobranzaFacturaSerializer(many=True)

    class Meta:
        model = Cobranza
        fields = (
            'cliente', 'total',
            'cobranza_facturas',
        )

    def validate_cliente(self, data):
        try:
            cliente = Cliente.objects.get(pk=data)
            self.context['cliente'] = cliente
        except Cliente.DoesNotExist:
            raise serializers.ValidationError('Client does not exist.')
        return data

    def create(self, data):
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
