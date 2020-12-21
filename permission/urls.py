"""Permission URLs."""

# Django
from django.urls import path

# Views
from permission.views.permissions import (
    PermissionCreateView, PermissionDeleteView, PermissionDetailView,
    PermissionListView, PermisoUpdateView
)
from permission.views.groups import (
    GroupListView, GroupCreateView, GroupDetailtView, GroupUpdateView, GroupDeleteView
)

urlpatterns = [
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
