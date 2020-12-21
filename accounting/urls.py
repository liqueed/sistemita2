"""Accounting URLs."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework import routers

# Views
from accounting.views.cobranzas import (
    CobranzaViewSet, CobranzaListView, CobranzaCreateTemplateView,
    CobranzaDetailView, CobranzaUpdateTemplateView, CobranzaDeleteView
)
from accounting.views.pagos import (
    PagoViewSet, PagoListView, PagoCreateTemplateView,
    PagoDetailView, PagoUpdateTemplateView, PagoDeleteView
)
from accounting.views.permissions import (
    PermissionCreateView, PermissionDeleteView, PermissionDetailView,
    PermissionListView, PermisoUpdateView
)
from accounting.views.groups import (
    GroupListView, GroupCreateView, GroupDetailtView, GroupUpdateView, GroupDeleteView
)

router = routers.DefaultRouter()
router.register(r'cobranza', CobranzaViewSet)
router.register(r'pago', PagoViewSet)

urlpatterns = [
    # API
    path(r'api/', include(router.urls)),

    # Cobranza cliente
    path('cobranza/', CobranzaListView.as_view(), name='cobranza-list'),
    path('cobranza/agregar', CobranzaCreateTemplateView.as_view(), name='cobranza-create'),
    path('cobranza/<int:pk>/', CobranzaDetailView.as_view(), name='cobranza-detail'),
    path('cobranza/<int:pk>/editar/', CobranzaUpdateTemplateView.as_view(), name='cobranza-update'),
    path('cobranza/<int:pk>/eliminar/', CobranzaDeleteView.as_view(), name='cobranza-delete'),

    # Pago a proveedor
    path('pago/', PagoListView.as_view(), name='pago-list'),
    path('pago/agregar', PagoCreateTemplateView.as_view(), name='pago-create'),
    path('pago/<int:pk>/', PagoDetailView.as_view(), name='pago-detail'),
    path('pago/<int:pk>/editar/', PagoUpdateTemplateView.as_view(), name='pago-update'),
    path('pago/<int:pk>/eliminar/', PagoDeleteView.as_view(), name='pago-delete'),

    # Permisos
    path('permiso/', PermissionListView.as_view(), name='permission-listado'),
    path('permiso/agregar', PermissionCreateView.as_view(), name='permission-agregar'),
    path('permiso/<int:pk>/', PermissionDetailView.as_view(), name='permission-detalle'),
    path('permiso/<int:pk>/editar/', PermisoUpdateView.as_view(), name='permission-modificar'),
    path('permiso/<int:pk>/eliminar/', PermissionDeleteView.as_view(), name='permission-eliminar'),

    # Grupos
    path('grupo/', GroupListView.as_view(), name='group-listado'),
    path('grupo/agregar', GroupCreateView.as_view(), name='group-agregar'),
    path('grupo/<int:pk>/', GroupDetailtView.as_view(), name='group-detalle'),
    path('grupo/<int:pk>/editar/', GroupUpdateView.as_view(), name='group-modificar'),
    path('grupo/<int:pk>/eliminar/', GroupDeleteView.as_view(), name='group-eliminar'),
]
