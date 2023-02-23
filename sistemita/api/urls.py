"""URLs API."""

# Django
# Django
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# API
from sistemita.api.archivos.views import ArchivoViewSet
from sistemita.api.clientes.views import (
    ClienteViewSet,
    ContratoViewSet,
    FacturaDistribuidaViewSet,
    FacturaImputadaViewSet,
    FacturaViewSet,
)
from sistemita.api.cobranzas.views import CobranzaViewSet
from sistemita.api.entidades.views import DistritoViewSet, LocalidadViewSet
from sistemita.api.mediopago.views import MedioPagoViewSet
from sistemita.api.pagos.views import PagoViewSet
from sistemita.api.proveedores.views import (
    FacturaProveedorImputadaViewSet,
    FacturaProveedorViewSet,
    ProveedorViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# Core
router.register(r'archivo', ArchivoViewSet)
router.register(r'cliente', ClienteViewSet)
router.register(r'contrato', ContratoViewSet)
router.register(r'distrito', DistritoViewSet)
router.register(r'factura', FacturaViewSet)
router.register(r'factura-distribuida', FacturaDistribuidaViewSet)
router.register(r'factura-imputada', FacturaImputadaViewSet)
router.register(r'factura-proveedor', FacturaProveedorViewSet)
router.register(r'localidad', LocalidadViewSet)
router.register(r'proveedor', ProveedorViewSet)
router.register(r'facturaproveedor-imputada', FacturaProveedorImputadaViewSet)
router.register(r'mediopago', MedioPagoViewSet)

# Accounting
router.register(r'cobranza', CobranzaViewSet)
router.register(r'pago', PagoViewSet)

app_name = "api"
urlpatterns = router.urls
