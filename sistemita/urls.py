"""URLs de sistemita."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

# Views
from core.views.archivos import ArchivoViewSet
from core.views.clientes import (
    ClienteViewSet, ClienteListView, ClienteCreateView, ClienteDetailView, ClienteUpdateView,
    ClienteDeleteView
)
from core.views.distritos import DistritoViewSet
from core.views.facturascliente import (
    FacturaViewSet, FacturaListView, FacturaCreateView, FacturaDetailView, FacturaUpdateView,
    FacturaDeleteView
)
from core.views.facturasproveedor import (
    FacturaProveedorViewSet, FacturaProveedorListView, FacturaProveedorDetalleView,
    FacturaProveedorAgregarView, FacturaProveedorModificarView, FacturaProveedorEliminarView
)
from core.views.home import HomeView, error_403
from core.views.localidades import LocalidadViewSet
from core.views.mediopago import (
    MedioPagoListView, MedioPagoAgregarView, MedioPagoDetalleView,
    MedioPagoEliminarView, MedioPagoModificarView, MedioPagoViewSet
)
from core.views.proveedores import (
    ProveedorListView, ProveedorDetalleView, ProveedorAgregarView,
    ProveedorModificarView, ProveedorEliminarView, ProveedorViewSet
)
from core.views.ordencompra import (
    OrdenCompraListView, OrdenCompraCreateView, OrdenCompraDetailView, OrdenCompraUpdateView,
    OrdenCompraDeleteView
)
from core.views.usuarios import UsuarioListView

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
    # path('admin/', admin.site.urls),
    # path('', include('facturacion_clientes.urls'))

    # Account
    path('accounts/', include('django.contrib.auth.urls')),

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
    path('factura/<int:pk>/editar/', FacturaUpdateView.as_view(), name='factura-modificar'),
    path('factura/<int:pk>/eliminar/', FacturaDeleteView.as_view(), name='factura-eliminar'),

    path('ordencompra/', OrdenCompraListView.as_view(), name='ordencompra-list'),
    path('ordencompra/agregar/', OrdenCompraCreateView.as_view(), name='ordencompra-create'),
    path('ordencompra/<int:pk>/', OrdenCompraDetailView.as_view(), name='ordencompra-detail'),
    path('ordencompra/<int:pk>/editar/', OrdenCompraUpdateView.as_view(),
         name='ordencompra-update'),
    path('ordencompra/<int:pk>/eliminar/', OrdenCompraDeleteView.as_view(),
         name='ordencompra-delete'),

    # Proveedores
    path('proveedor/', ProveedorListView.as_view(), name='proveedor-listado'),
    path('proveedor/<int:pk>/', ProveedorDetalleView.as_view(), name='proveedor-detalle'),
    path('proveedor/<int:pk>/editar/', ProveedorModificarView.as_view(), name='proveedor-modificar'),
    path('proveedor/<int:pk>/eliminar/', ProveedorEliminarView.as_view(), name='proveedor-eliminar'),
    path('proveedor/agregar/', ProveedorAgregarView.as_view(), name='proveedor-agregar'),

    path('factura-proveedor/', FacturaProveedorListView.as_view(), name='factura-proveedor-listado'),
    path('factura-proveedor/<int:pk>/', FacturaProveedorDetalleView.as_view(), name='factura-proveedor-detalle'),
    path('factura-proveedor/<int:pk>/editar/', FacturaProveedorModificarView.as_view(), name='factura-proveedor-modificar'),
    path('factura-proveedor/<int:pk>/eliminar/', FacturaProveedorEliminarView.as_view(), name='factura-proveedor-eliminar'),
    path('factura-proveedor/agregar/', FacturaProveedorAgregarView.as_view(), name='factura-proveedor-agregar'),

    # Medio de pago
    path('mediopago/', MedioPagoListView.as_view(), name='mediopago-listado'),
    path('mediopago/agregar/', MedioPagoAgregarView.as_view(), name='mediopago-agregar'),
    path('mediopago/<int:pk>/', MedioPagoDetalleView.as_view(), name='mediopago-detalle'),
    path('mediopago/<int:pk>/editar/', MedioPagoModificarView.as_view(), name='mediopago-modificar'),
    path('medio/<int:pk>/eliminar/', MedioPagoEliminarView.as_view(), name='mediopago-eliminar'),

    # Usuarios
    path('usuarios/', UsuarioListView.as_view(), name='usuario-list'),

    # Accounting module
    path('', include(('accounting.urls', 'accounting'), namespace='accounting')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
