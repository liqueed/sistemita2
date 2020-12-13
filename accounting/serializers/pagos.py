"""Modulo serializers de pagos."""

# Django REST Framework
from rest_framework import serializers

# Serialize
from core.serializers import ProveedorSerializer

# Models
from core.models.proveedor import Proveedor, FacturaProveedor
from accounting.models.pago import (
    Pago, PagoFactura, PagoFacturaPago
)


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
        fields = (
            'id', 'data',
            'factura', 'ganancias', 'ingresos_brutos', 'iva',
            'pago_factura_pagos'
        )
        read_only_fields = ('id',)


class PagoSerializer(serializers.ModelSerializer):
    """Pago Serializer."""
    proveedor = ProveedorSerializer()
    total = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)
    pago_facturas = PagoFacturaSerializer(many=True)

    class Meta:
        """Clase meta."""
        model = Pago
        fields = (
            'id', 'proveedor', 'total',
            'pago_facturas',
        )
        read_only_fields = ('id', 'proveedor')

    def validate_proveedor(self, data):
        """Valida datos de proveedor."""
        try:
            proveedor = Proveedor.objects.get(cuit=data['cuit'])
            self.context['proveedor'] = proveedor
        except Proveedor.DoesNotExist:
            raise serializers.ValidationError('Proveedor does not exist.')
        return data

    def create(self, data):
        """Genera un pago con factura/s y su/s correspondiente/s pago/s."""
        try:
            # Factura
            proveedor = self.context['proveedor']
            total = data['total']
            pago = Pago.objects.create(proveedor=proveedor, total=total)

            # Factura pago
            facturas = data['pago_facturas']
            for factura in facturas:
                # La factura pasa a estar cobrada
                factura_entry = factura['factura']
                FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=True)

                pago_factura = PagoFactura.objects.create(
                    pago=pago,
                    factura=factura_entry,
                    ganancias=factura['ganancias'],
                    ingresos_brutos=factura['ingresos_brutos'],
                    iva=factura['iva']
                )
                # Pagos
                pagos = factura['pago_factura_pagos']
                for row in pagos:
                    PagoFacturaPago.objects.create(
                        pago_factura=pago_factura,
                        metodo=row['metodo'],
                        monto=row['monto']
                    )
            return pago
        except Exception as error:
            raise serializers.ValidationError(error)

    def update(self, instance, data):
        try:
            instance.total = data['total']
            facturas = data['pago_facturas']

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
                        iva=factura['iva']
                    )

                    # pagos
                    pagos = factura['pago_factura_pagos']
                    for row in pagos:
                        # Todos los pagos son nuevos al ser nueva la factura
                        PagoFacturaPago.objects.create(
                            pago_factura=pago_factura,
                            metodo=row['metodo'],
                            monto=row['monto']
                        )
                elif factura['data']['action'] == 'update':
                    # Actualizo factura del pago
                    pago_factura = PagoFactura.objects.get(
                        pk=factura['data']['id']  # data contiene la pk de la factura de pago
                    )

                    factura_entry = factura['factura']
                    if pago_factura.factura.id != factura_entry.id:
                        # Si la factura es diferente, la anterior pasa a estar no cobrada
                        FacturaProveedor.objects.filter(pk=pago_factura.factura.id).update(
                            cobrado=False
                        )

                    # La factura actual del proveedor pasa a estar cobrada
                    FacturaProveedor.objects.filter(pk=factura_entry.id).update(cobrado=True)

                    PagoFactura.objects.filter(pk=factura_entry.id).update(
                        factura=factura_entry,
                        ganancias=factura['ganancias'],
                        ingresos_brutos=factura['ingresos_brutos'],
                        iva=factura['iva']
                    )

                    # Pagos
                    pagos = factura['pago_factura_pagos']
                    for row in pagos:
                        if row['data']['action'] == 'update':
                            # Actualiza pago
                            PagoFacturaPago.objects.filter(pk=row['data']['id']).update(
                                metodo=row['metodo'],
                                monto=row['monto']
                            )
                        elif row['data']['action'] == 'add':
                            # Agrega Pago
                            PagoFacturaPago.objects.create(
                                pago_factura=pago_factura,
                                metodo=row['metodo'],
                                monto=row['monto']
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
