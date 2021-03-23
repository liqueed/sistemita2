"""Modúlo para generar exportaciones de datos."""

# Imports
import csv
import io

# Datetime
from datetime import datetime

# Django
from django.db.models import Sum
from django.http import HttpResponse

# Utils
from core.constants import MONEDAS
import xlsxwriter


class FacturaExport:
    """Clase para exportar facturas.

    Args:
       queryset (django.queryset): QuerySet de Django.
    """

    def __init__(self, queryset):
        """Inicialización de variables."""
        self.queryset = queryset
        self.app_name = queryset.model.__name__.lower()

    def __str__(self):
        """Configuraciones de la clase."""
        return self.__class__.__name__

    def get_debt_by_moneda(self, moneda):
        """Devuelve un total con la suma de las facturas adeudadas por moneda.

        Args:
            moneda (str): Moneda de tipo '$' o 'U$D'.

        Return:
            str: Moneda y sumatoria del monto adeudado del total de facturas.
        """
        moneda_type = 'P' if moneda == '$' else 'D'
        result = self.queryset.filter(cobrado=False, moneda=moneda_type).aggregate(
            Sum('total')
        )

        return '{} {}'.format(moneda, result['total__sum'] or 0)


class FacturaClienteExport(FacturaExport):
    """Clase para exportar facturas de clientes.

    Args:
       queryset (django.queryset): queryset de factura de clientes.
    """

    def __init__(self, queryset):
        """Inicialización de variables."""
        FacturaExport.__init__(self, queryset.order_by('fecha'))
        self.headers = [
            'fecha', 'numero', 'tipo', 'cliente', 'neto', 'iva', 'total', 'cobrado'
        ]

    def get_data(self):
        """Devuelve una lista de facturas de clientes.

        Returns:
           list: Obtiene el queryset y genera un lista.
        """
        data = []

        for item in self.queryset:
            cobrado = 'Si' if item.cobrado else 'No'
            moneda_neto = '{} {}'.format(item.get_moneda_display(), str(item.neto))
            data.append([
                item.fecha.strftime('%d/%m/%Y'), item.numero, item.get_tipo(), item.cliente.razon_social,
                moneda_neto, item.iva, item.moneda_monto, cobrado
            ])
        return data


class FacturaProveedorExport(FacturaExport):
    """Clase para exportar facturas de proveedores.

    Args:
       queryset (django.queryset): queryset de facturas de proveedor.
    """

    def __init__(self, queryset):
        """Inicialización de variables."""
        FacturaExport.__init__(self, queryset.order_by('fecha'))
        self.headers = [
            'fecha', 'numero', 'tipo', 'proveedor', 'neto', 'iva', 'total', 'pagado',
            'factura_cliente_fecha', 'cliente', 'factura_cliente_nro', 'factura_cliente_tipo',
            'factura_cliente_neto', 'factura_cliente_iva', 'factura_cliente_total',
            'factura_cliente_cobrado'
        ]

    def get_data(self):
        """Devuelve una lista de facturas de proveedor.

        Returns:
           list: Obtiene el queryset y genera un lista.
        """
        data = []

        for item in self.queryset:
            cobrado = 'Si' if item.cobrado else 'No'
            cobrado_cliente = 'Si' if item.factura.cobrado else 'No'
            data.append([
                item.fecha.strftime('%d/%m/%Y'), item.numero, item.get_tipo(), item.proveedor.razon_social,
                item.moneda_monto, item.iva, item.moneda_monto, cobrado,
                item.factura.fecha.strftime('%d/%m/%Y'), item.factura.cliente.razon_social, item.factura.numero,
                item.factura.get_tipo(), item.factura.moneda_monto, item.factura.iva, item.factura.total,
                cobrado_cliente
            ])
        return data


class PagoExport():
    """Clase para exportar pagos a proveedores.

    Args:
       queryset (django.queryset): queryset de pagos a proveedor.
    """

    def __init__(self, queryset):
        """Inicialización de variables."""
        self.queryset = queryset.order_by('fecha')
        self.headers = [
            'pago_nro', 'fecha', 'proveedor', 'total', 'pagado',
        ]

    def get_data(self):
        """Devuelve una lista de pagos a proveedores.

        Returns:
           list: Obtiene el queryset y genera un lista.
        """
        data = []

        for item in self.queryset:
            pagado = 'Si' if item.pagado else 'No'
            data.append([
                item.pk, item.fecha.strftime('%d/%m/%Y'), item.proveedor.razon_social,
                item.total, pagado
            ])
        return data

    def get_debt_by_moneda(self, moneda):
        """Devuelve un total con la suma de las facturas adeudadas por moneda.

        Args:
            moneda (str): Moneda de tipo '$' o 'U$D'.

        Return:
            str: Moneda y sumatoria del monto adeudado del total de facturas.
        """
        result = {'total__sum': None}
        if moneda == '$':
            result = self.queryset.filter(pagado=False).aggregate(
                Sum('total')
            )

        return '{} {}'.format(moneda, result['total__sum'] or 0)


class PagoRetencionExport():
    """Clase para exportar retenciones de pagos a proveedores.

    Args:
       queryset (django.queryset): queryset de pagos a proveedor.
    """

    def __init__(self, queryset):
        """Inicialización de variables."""
        self.queryset = queryset.order_by('fecha')
        self.headers = [
            'pago_nro', 'fecha', 'proveedor', 'retencion_ganancia', 'retencion_ingresos_brutos', 'retencion_iva',
        ]

    def get_data(self):
        """Devuelve una lista de pagos a proveedores.

        Returns:
           list: Obtiene el queryset y genera un lista.
        """
        data = []

        for item in self.queryset:
            data.append([
                item.pk, item.fecha.strftime('%d/%m/%Y'), item.proveedor.razon_social,
                item.pago_facturas.all()[0].ganancias, item.pago_facturas.all()[0].ingresos_brutos,
                item.pago_facturas.all()[0].iva
            ])
            for factura in item.pago_facturas.all()[1:]:
                data.append([
                    '', '', '', factura.ganancias, factura.ingresos_brutos, factura.iva
                ])
        return data


def export_excel(request, queryset):
    """Devuelve un archivo en formato excel.

    Args:
       request (django.request): Request GET de Django.
       queryset (django.queryset): QuerySet de Django.

    Returns:
       response (HttpResponse): Un archivo en formato excel.
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    display_dept = False
    bold = workbook.add_format({'bold': True})

    app = queryset.model.__name__.lower()

    if app == 'factura':
        app_export = FacturaClienteExport(queryset)
        display_dept = True
    elif app == 'facturaproveedor':
        app_export = FacturaProveedorExport(queryset)
        display_dept = True
    elif app == 'pago' and request.GET.get('tipo') == 'retenciones':
        app_export = PagoRetencionExport(queryset)
        display_dept = False
    elif app == 'pago':
        app_export = PagoExport(queryset)
        display_dept = True

    # Encabezados
    for col_num, data in enumerate(app_export.headers):
        worksheet.write(0, col_num, data, bold)

    # Datos
    data = app_export.get_data()
    for row_num, columns in enumerate(data):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num + 1, col_num, cell_data)

    # Deuda
    if display_dept:
        worksheet.write(len(data) + 2, 0, 'Total adeudado', bold)
        worksheet.write(len(data) + 2, 1, '{}'.format(app_export.get_debt_by_moneda(MONEDAS[0][1])), bold)
        worksheet.write(len(data) + 2, 2, '{}'.format(app_export.get_debt_by_moneda(MONEDAS[1][1])), bold)

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename={}_{}.xlsx'.format(
        app, datetime.now().strftime('%d%m%Y')
    )

    return response


def export_csv(request, queryset):
    """Devuelve un archivo en formato CSV."""
    app = queryset.model.__name__.lower()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(app)

    if app == 'factura':
        app_export = FacturaClienteExport(queryset)
    else:
        app_export = FacturaProveedorExport(queryset)

    writer = csv.writer(response)
    writer.writerow(app_export.headers)  # primer fila con los encabezados
    data = app_export.get_data()

    for item in data:
        writer.writerow(item)

    return response
