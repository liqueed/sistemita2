"""Accounting URLs."""

# Django
from django.urls import path

# Views
from sistemita.accounting.views.cobranzas import (
    CobranzaCreateTemplateView,
    CobranzaDeleteView,
    CobranzaDetailView,
    CobranzaListView,
    CobranzaUpdateTemplateView,
)
from sistemita.accounting.views.pagos import (
    PagoCreateTemplateView,
    PagoDeleteView,
    PagoDetailView,
    PagoFacturaRetencionGeratePDFDetailView,
    PagoGeratePDFDetailView,
    PagoListView,
    PagoUpdateTemplateView,
)

urlpatterns = [
    # Cobranza cliente
    path('cobranza/', CobranzaListView.as_view(), name='cobranza-list'),
    path('cobranza/agregar/', CobranzaCreateTemplateView.as_view(), name='cobranza-create'),
    path('cobranza/<int:pk>/', CobranzaDetailView.as_view(), name='cobranza-detail'),
    path('cobranza/<int:pk>/editar/', CobranzaUpdateTemplateView.as_view(), name='cobranza-update'),
    path('cobranza/<int:pk>/eliminar/', CobranzaDeleteView.as_view(), name='cobranza-delete'),
    # Pago a proveedor
    path('pago/', PagoListView.as_view(), name='pago-list'),
    path('pago/agregar/', PagoCreateTemplateView.as_view(), name='pago-create'),
    path('pago/<int:pk>/', PagoDetailView.as_view(), name='pago-detail'),
    path('pago/<int:pk>/editar/', PagoUpdateTemplateView.as_view(), name='pago-update'),
    path('pago/<int:pk>/eliminar/', PagoDeleteView.as_view(), name='pago-delete'),
    path('pago/<int:pk>/comprobante/', PagoGeratePDFDetailView.as_view(), name='pago-generate-pdf'),
    path(
        'pago/<int:pk>/comprobante-retencion/',
        PagoFacturaRetencionGeratePDFDetailView.as_view(),
        name='pago-factura-retencion-pdf',
    ),
]
