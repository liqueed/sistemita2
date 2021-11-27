"""URLs API."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework import routers

# API
from sistemita.api.archivos.views import ArchivoViewSet
from sistemita.api.clientes.views import (
    ClienteViewSet,
    FacturaImputadaViewSet,
    FacturaViewSet,
)
from sistemita.api.cobranzas.views import CobranzaViewSet
from sistemita.api.entidades.views import DistritoViewSet, LocalidadViewSet
from sistemita.api.mediopago.views import MedioPagoViewSet
from sistemita.api.pagos.views import PagoViewSet
from sistemita.api.proveedores.views import (
    FacturaProveedorViewSet,
    ProveedorViewSet,
)

router = routers.DefaultRouter()

# Core
router.register(r'archivo', ArchivoViewSet)
router.register(r'cliente', ClienteViewSet)
router.register(r'distrito', DistritoViewSet)
router.register(r'factura', FacturaViewSet)
router.register(r'factura-imputada', FacturaImputadaViewSet)
router.register(r'factura-proveedor', FacturaProveedorViewSet)
router.register(r'localidad', LocalidadViewSet)
router.register(r'proveedor', ProveedorViewSet)
router.register(r'mediopago', MedioPagoViewSet)

# Accounting
router.register(r'cobranza', CobranzaViewSet)
router.register(r'pago', PagoViewSet)

urlpatterns = [
    path(r'api/', include(router.urls)),
]
