"""URLs Core."""

# Django
from django.urls import path

# Views
from sistemita.core.views.clientes import (
    ClienteCreateView,
    ClienteDeleteView,
    ClienteDetailView,
    ClienteListView,
    ClienteUpdateView,
)
from sistemita.core.views.facturascategoria import (
    FacturaCategoriaCreateView,
    FacturaCategoriaDeleteView,
    FacturaCategoriaDetailView,
    FacturaCategoriaListView,
    FacturaCategoriaUpdateView,
)
from sistemita.core.views.facturascliente import (
    FacturaCreateView,
    FacturaDeleteView,
    FacturaDetailView,
    FacturaImportTemplateView,
    FacturaListView,
    FacturaUpdateView,
)
from sistemita.core.views.facturasimputada import (
    FacturaImputadaCreateTemplateView,
    FacturaImputadaDeleteView,
    FacturaImputadaDetailView,
    FacturaImputadaListView,
    FacturaImputadaUpdateTemplateView,
)
from sistemita.core.views.facturasproveedor import (
    FacturaProveedorByUserDetailView,
    FacturaProveedorByUserListView,
    FacturaProveedorCreateView,
    FacturaProveedorDeleteView,
    FacturaProveedorDetailView,
    FacturaProveedorImportTemplateView,
    FacturaProveedorListView,
    FacturaProveedorReportListView,
    FacturaProveedorUpdateView,
)
from sistemita.core.views.facturasproveedorcategoria import (
    FacturaProveedorCategoriaCreateView,
    FacturaProveedorCategoriaDeleteView,
    FacturaProveedorCategoriaDetailView,
    FacturaProveedorCategoriaListView,
    FacturaProveedorCategoriaUpdateView,
)
from sistemita.core.views.facturasproveedorimputada import (
    FacturaProveedorImputadaCreateTemplateView,
    FacturaProveedorImputadaDeleteView,
    FacturaProveedorImputadaDetailView,
    FacturaProveedorImputadaListView,
    FacturaProveedorImputadaUpdateTemplateView,
)
from sistemita.core.views.home import HomeView, error_403, error_404, error_500
from sistemita.core.views.mediopago import (
    MedioPagoCreateView,
    MedioPagoDeleteView,
    MedioPagoDetailView,
    MedioPagoListView,
    MedioPagoUpdateView,
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
)

handler400 = error_403
handler404 = error_404
handler500 = error_500

app_name = 'core'
urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='home'),
    # Cliente
    path('cliente/', ClienteListView.as_view(), name='cliente-list'),
    path('cliente/agregar/', ClienteCreateView.as_view(), name='cliente-create'),
    path('cliente/<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('cliente/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('cliente/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente-delete'),
    # Factura
    path('factura/', FacturaListView.as_view(), name='factura-list'),
    path('factura/agregar/', FacturaCreateView.as_view(), name='factura-create'),
    path('factura/<int:pk>/', FacturaDetailView.as_view(), name='factura-detail'),
    path('factura/<int:pk>/editar/', FacturaUpdateView.as_view(), name='factura-update'),
    path('factura/<int:pk>/eliminar/', FacturaDeleteView.as_view(), name='factura-delete'),
    path('factura/importar/', FacturaImportTemplateView.as_view(), name='factura-import'),
    # Factura categoría
    path('facturacategoria/', FacturaCategoriaListView.as_view(), name='facturacategoria-list'),
    path('facturacategoria/agregar/', FacturaCategoriaCreateView.as_view(), name='facturacategoria-create'),
    path('facturacategoria/<int:pk>/', FacturaCategoriaDetailView.as_view(), name='facturacategoria-detail'),
    path('facturacategoria/<int:pk>/editar/', FacturaCategoriaUpdateView.as_view(), name='facturacategoria-update'),
    path('facturacategoria/<int:pk>/eliminar/', FacturaCategoriaDeleteView.as_view(), name='facturacategoria-delete'),
    # Factura imputada
    path('facturaimputada/', FacturaImputadaListView.as_view(), name='facturaimputada-list'),
    path('facturaimputada/agregar/', FacturaImputadaCreateTemplateView.as_view(), name='facturaimputada-create'),
    path('facturaimputada/<int:pk>/', FacturaImputadaDetailView.as_view(), name='facturaimputada-detail'),
    path(
        'facturaimputada/<int:pk>/editar/', FacturaImputadaUpdateTemplateView.as_view(), name='facturaimputada-update'
    ),
    path('facturaimputada/<int:pk>/eliminar/', FacturaImputadaDeleteView.as_view(), name='facturaimputada-delete'),
    # Orden de compra
    path('ordencompra/', OrdenCompraListView.as_view(), name='ordencompra-list'),
    path('ordencompra/agregar/', OrdenCompraCreateView.as_view(), name='ordencompra-create'),
    path('ordencompra/<int:pk>/', OrdenCompraDetailView.as_view(), name='ordencompra-detail'),
    path('ordencompra/<int:pk>/editar/', OrdenCompraUpdateView.as_view(), name='ordencompra-update'),
    path('ordencompra/<int:pk>/eliminar/', OrdenCompraDeleteView.as_view(), name='ordencompra-delete'),
    # Proveedores
    path('proveedor/', ProveedorListView.as_view(), name='proveedor-list'),
    path('proveedor/agregar/', ProveedorCreateView.as_view(), name='proveedor-create'),
    path('proveedor/<int:pk>/', ProveedorDetailView.as_view(), name='proveedor-detail'),
    path('proveedor/<int:pk>/editar/', ProveedorUpdateView.as_view(), name='proveedor-update'),
    path('proveedor/<int:pk>/eliminar/', ProveedorDeleteView.as_view(), name='proveedor-delete'),
    # Factura de proveedores
    path('factura-proveedor/', FacturaProveedorListView.as_view(), name='facturaproveedor-list'),
    path(
        'factura-proveedor/mis-facturas/',
        FacturaProveedorByUserListView.as_view(),
        name='facturaproveedor-list-by-user',
    ),
    path(
        'factura-proveedor/mis-facturas/<int:pk>/',
        FacturaProveedorByUserDetailView.as_view(),
        name='facturaproveedor-detail-by-user',
    ),
    path('factura-proveedor/agregar/', FacturaProveedorCreateView.as_view(), name='facturaproveedor-create'),
    path('factura-proveedor/<int:pk>/', FacturaProveedorDetailView.as_view(), name='facturaproveedor-detail'),
    path('factura-proveedor/<int:pk>/editar/', FacturaProveedorUpdateView.as_view(), name='facturaproveedor-update'),
    path('factura-proveedor/<int:pk>/eliminar/', FacturaProveedorDeleteView.as_view(), name='facturaproveedor-delete'),
    path('factura-proveedor/importar/', FacturaProveedorImportTemplateView.as_view(), name='facturaproveedor-import'),
    path('factura-proveedor/reporte-ventas/', FacturaProveedorReportListView.as_view(), name='facturaproveedor-report'),
    # Facturas categorías
    path(
        'facturaproveedorcategoria/', FacturaProveedorCategoriaListView.as_view(), name='facturaproveedorcategoria-list'
    ),
    path(
        'facturaproveedorcategoria/agregar/',
        FacturaProveedorCategoriaCreateView.as_view(),
        name='facturaproveedorcategoria-create',
    ),
    path(
        'facturaproveedorcategoria/<int:pk>/',
        FacturaProveedorCategoriaDetailView.as_view(),
        name='facturaproveedorcategoria-detail',
    ),
    path(
        'facturaproveedorcategoria/<int:pk>/editar/',
        FacturaProveedorCategoriaUpdateView.as_view(),
        name='facturaproveedorcategoria-update',
    ),
    path(
        'facturaproveedorcategoria/<int:pk>/eliminar/',
        FacturaProveedorCategoriaDeleteView.as_view(),
        name='facturaproveedorcategoria-delete',
    ),
    # Factura de proveedores imputada
    path('facturaproveedorimputada/', FacturaProveedorImputadaListView.as_view(), name='facturaproveedorimputada-list'),
    path(
        'facturaproveedorimputada/agregar/',
        FacturaProveedorImputadaCreateTemplateView.as_view(),
        name='facturaproveedorimputada-create',
    ),
    path(
        'facturaproveedorimputada/<int:pk>/',
        FacturaProveedorImputadaDetailView.as_view(),
        name='facturaproveedorimputada-detail',
    ),
    path(
        'facturaproveedorimputada/<int:pk>/editar/',
        FacturaProveedorImputadaUpdateTemplateView.as_view(),
        name='facturaproveedorimputada-update',
    ),
    path(
        'facturaproveedorimputada/<int:pk>/eliminar/',
        FacturaProveedorImputadaDeleteView.as_view(),
        name='facturaproveedorimputada-delete',
    ),
    # Medio de pago
    path('mediopago/', MedioPagoListView.as_view(), name='mediopago-list'),
    path('mediopago/agregar/', MedioPagoCreateView.as_view(), name='mediopago-create'),
    path('mediopago/<int:pk>/', MedioPagoDetailView.as_view(), name='mediopago-detail'),
    path('mediopago/<int:pk>/editar/', MedioPagoUpdateView.as_view(), name='mediopago-update'),
    path('mediopago/<int:pk>/eliminar/', MedioPagoDeleteView.as_view(), name='mediopago-delete'),
]
