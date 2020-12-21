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
    FacturaViewSet, FacturaModificarView, FacturaListView, FacturaEliminarView,
    FacturaDetalleView, FacturaAgregarView
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
    OrdenCompraListView, OrdenCompraDetalleView, OrdenCompraModificarView,
    OrdenCompraEliminarView, OrdenCompraAgregarView
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

    path('factura/', FacturaListView.as_view(), name='factura-listado'),
    path('factura/<int:pk>/', FacturaDetalleView.as_view(), name='factura-detalle'),
    path('factura/<int:pk>/editar/', FacturaModificarView.as_view(), name='factura-modificar'),
    path('factura/<int:pk>/eliminar/', FacturaEliminarView.as_view(), name='factura-eliminar'),
    path('factura/agregar/', FacturaAgregarView.as_view(), name='factura-agregar'),

    path('ordencompra/', OrdenCompraListView.as_view(), name='ordencompra-listado'),
    path('ordencompra/<int:pk>/', OrdenCompraDetalleView.as_view(), name='ordencompra-detalle'),
    path('ordencompra/<int:pk>/editar/', OrdenCompraModificarView.as_view(), name='ordencompra-modificar'),
    path('ordencompra/<int:pk>/eliminar/', OrdenCompraEliminarView.as_view(), name='ordencompra-eliminar'),
    path('ordencompra/agregar/', OrdenCompraAgregarView.as_view(), name='ordencompra-agregar'),

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
