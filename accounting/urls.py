"""Accounting URLs."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework import routers

# Views
from accounting.views.cobranzas import (
    CobranzaViewSet, CobranzaListView, CobranzaAgregarTemplateView,
    CobranzaDetalleView, CobranzaEditarTemplateView, CobranzaEliminarView
)
from accounting.views.pagos import (
    PagoViewSet, PagoListView, PagoAgregarTemplateView,
    PagoDetalleView, PagoEditarTemplateView, PagoEliminarView
)
from accounting.views.permissions import (
    PermissionCreateView, PermissionDeleteView, PermissionDetailView,
    PermissionListView, PermisoUpdateView
)

router = routers.DefaultRouter()
router.register(r'cobranza', CobranzaViewSet)
router.register(r'pago', PagoViewSet)

urlpatterns = [
    # API
    path(r'api/', include(router.urls)),

    # Cobranza cliente
    path('cobranza/', CobranzaListView.as_view(), name='cobranza-listado'),
    path('cobranza/agregar', CobranzaAgregarTemplateView.as_view(), name='cobranza-agregar'),
    path('cobranza/<int:pk>/', CobranzaDetalleView.as_view(), name='cobranza-detalle'),
    path('cobranza/<int:pk>/editar/', CobranzaEditarTemplateView.as_view(), name='cobranza-modificar'),
    path('cobranza/<int:pk>/eliminar/', CobranzaEliminarView.as_view(), name='cobranza-eliminar'),

    # Pago a proveedor
    path('pago/', PagoListView.as_view(), name='pago-listado'),
    path('pago/agregar', PagoAgregarTemplateView.as_view(), name='pago-agregar'),
    path('pago/<int:pk>/', PagoDetalleView.as_view(), name='pago-detalle'),
    path('pago/<int:pk>/editar/', PagoEditarTemplateView.as_view(), name='pago-modificar'),
    path('pago/<int:pk>/eliminar/', PagoEliminarView.as_view(), name='pago-eliminar'),

    # Permisos
    path('permiso/', PermissionListView.as_view(), name='permission-listado'),
    path('permiso/agregar', PermissionCreateView.as_view(), name='permission-agregar'),
    path('permiso/<int:pk>/', PermissionDetailView.as_view(), name='permission-detalle'),
    path('permiso/<int:pk>/editar/', PermisoUpdateView.as_view(), name='permission-modificar'),
    path('permiso/<int:pk>/eliminar/', PermissionDeleteView.as_view(), name='permission-eliminar'),
]
