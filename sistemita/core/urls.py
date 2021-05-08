"""URLs Core."""

from django.urls import include, path
from rest_framework import routers

# Views
from sistemita.core.views.archivos import ArchivoViewSet
from sistemita.core.views.clientes import (
    ClienteCreateView,
    ClienteDeleteView,
    ClienteDetailView,
    ClienteListView,
    ClienteUpdateView,
    ClienteViewSet,
)
from sistemita.core.views.distritos import DistritoViewSet
from sistemita.core.views.facturascliente import (
    FacturaCreateView,
    FacturaDeleteView,
    FacturaDetailView,
    FacturaListView,
    FacturaUpdateView,
    FacturaViewSet,
)
from sistemita.core.views.facturasproveedor import (
    FacturaProveedorCreateView,
    FacturaProveedorDeleteView,
    FacturaProveedorDetailView,
    FacturaProveedorListView,
    FacturaProveedorReportListView,
    FacturaProveedorUpdateView,
    FacturaProveedorViewSet,
)
from sistemita.core.views.home import HomeView, error_403
from sistemita.core.views.localidades import LocalidadViewSet
from sistemita.core.views.mediopago import (
    MedioPagoCreateView,
    MedioPagoDeleteView,
    MedioPagoDetailView,
    MedioPagoListView,
    MedioPagoUpdateView,
    MedioPagoViewSet,
)
from sistemita.core.views.ordencompra import (
    OrdenCompraCreateView,
    OrdenCompraDeleteView,
    OrdenCompraDetailView,
    OrdenCompraListView,
    OrdenCompraUpdateView,
)
from sistemita.core.views.proveedores import (
    ProveedorCreateView,
    ProveedorDeleteView,
    ProveedorDetailView,
    ProveedorListView,
    ProveedorUpdateView,
    ProveedorViewSet,
)

router = routers.DefaultRouter()
router.register(r'archivo', ArchivoViewSet)
router.register(r'cliente', ClienteViewSet)
router.register(r'distrito', DistritoViewSet)
router.register(r'factura', FacturaViewSet)
router.register(r'factura-proveedor', FacturaProveedorViewSet)
router.register(r'localidad', LocalidadViewSet)
router.register(r'proveedor', ProveedorViewSet)
router.register(r'mediopago', MedioPagoViewSet)

handler400 = error_403

urlpatterns = [

    # Home
    path('', HomeView.as_view(), name='home'),

    # API
    path(r'api/', include(router.urls)),

    # Cliente
    path('cliente/', ClienteListView.as_view(), name='cliente-list'),
    path('cliente/agregar/', ClienteCreateView.as_view(), name='cliente-create'),
    path('cliente/<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('cliente/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('cliente/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente-delete'),

    path('factura/', FacturaListView.as_view(), name='factura-list'),
    path('factura/agregar/', FacturaCreateView.as_view(), name='factura-create'),
    path('factura/<int:pk>/', FacturaDetailView.as_view(), name='factura-detail'),
    path('factura/<int:pk>/editar/', FacturaUpdateView.as_view(), name='factura-update'),
    path('factura/<int:pk>/eliminar/', FacturaDeleteView.as_view(), name='factura-delete'),

    path('ordencompra/', OrdenCompraListView.as_view(), name='ordencompra-list'),
    path('ordencompra/agregar/', OrdenCompraCreateView.as_view(), name='ordencompra-create'),
    path('ordencompra/<int:pk>/', OrdenCompraDetailView.as_view(), name='ordencompra-detail'),
    path('ordencompra/<int:pk>/editar/', OrdenCompraUpdateView.as_view(),
         name='ordencompra-update'),
    path('ordencompra/<int:pk>/eliminar/', OrdenCompraDeleteView.as_view(),
         name='ordencompra-delete'),

    # Proveedores
    path('proveedor/', ProveedorListView.as_view(), name='proveedor-list'),
    path('proveedor/agregar/', ProveedorCreateView.as_view(), name='proveedor-create'),
    path('proveedor/<int:pk>/', ProveedorDetailView.as_view(), name='proveedor-detail'),
    path('proveedor/<int:pk>/editar/', ProveedorUpdateView.as_view(), name='proveedor-update'),
    path('proveedor/<int:pk>/eliminar/', ProveedorDeleteView.as_view(), name='proveedor-delete'),

    path('factura-proveedor/', FacturaProveedorListView.as_view(), name='facturaproveedor-list'),
    path('factura-proveedor/agregar/', FacturaProveedorCreateView.as_view(),
         name='facturaproveedor-create'),
    path('factura-proveedor/<int:pk>/', FacturaProveedorDetailView.as_view(),
         name='facturaproveedor-detail'),
    path('factura-proveedor/<int:pk>/editar/', FacturaProveedorUpdateView.as_view(),
         name='facturaproveedor-update'),
    path('factura-proveedor/<int:pk>/eliminar/', FacturaProveedorDeleteView.as_view(),
         name='facturaproveedor-delete'),
    path('factura-proveedor/reporte-ventas/', FacturaProveedorReportListView.as_view(), name='facturaproveedor-report'),

    # Medio de pago
    path('mediopago/', MedioPagoListView.as_view(), name='mediopago-list'),
    path('mediopago/agregar/', MedioPagoCreateView.as_view(), name='mediopago-create'),
    path('mediopago/<int:pk>/', MedioPagoDetailView.as_view(), name='mediopago-detail'),
    path('mediopago/<int:pk>/editar/', MedioPagoUpdateView.as_view(), name='mediopago-update'),
    path('medio/<int:pk>/eliminar/', MedioPagoDeleteView.as_view(), name='mediopago-delete'),
]
