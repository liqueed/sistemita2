"""Permission URLs."""

# Django
from django.urls import path

# Views
from authorization.views.groups import (
    GroupListView, GroupCreateView, GroupDetailtView, GroupUpdateView, GroupDeleteView
)
from authorization.views.permissions import (
    PermissionCreateView, PermissionDeleteView, PermissionDetailView,
    PermissionListView, PermisoUpdateView
)
from authorization.views.users import (
    UserListView, UserCreateFormView, UserDetailView, UserUpdateView, PasswordChangeFormView,
    UserDeleteView
)

urlpatterns = [
    # Usuarios
    path('usuario/', UserListView.as_view(), name='user-list'),
    path('usuario/agregar', UserCreateFormView.as_view(), name='user-create'),
    path('usuario/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('usuario/<int:pk>/editar/', UserUpdateView.as_view(), name='user-update'),
    path('usuario/<int:pk>/eliminar/', UserDeleteView.as_view(), name='user-delete'),
    path('usuario/<int:pk>/password/', PasswordChangeFormView.as_view(), name='user-pass'),

    # Grupos
    path('grupo/', GroupListView.as_view(), name='group-list'),
    path('grupo/agregar', GroupCreateView.as_view(), name='group-create'),
    path('grupo/<int:pk>/', GroupDetailtView.as_view(), name='group-detail'),
    path('grupo/<int:pk>/editar/', GroupUpdateView.as_view(), name='group-update'),
    path('grupo/<int:pk>/eliminar/', GroupDeleteView.as_view(), name='group-delete'),

    # Permiso
    path('permiso/', PermissionListView.as_view(), name='permission-list'),
    path('permiso/agregar', PermissionCreateView.as_view(), name='permission-create'),
    path('permiso/<int:pk>/', PermissionDetailView.as_view(), name='permission-detail'),
    path('permiso/<int:pk>/editar/', PermisoUpdateView.as_view(), name='permission-update'),
    path('permiso/<int:pk>/eliminar/', PermissionDeleteView.as_view(), name='permission-delete'),

]
