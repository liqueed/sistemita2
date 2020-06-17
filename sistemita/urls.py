from django.urls import path, include
from rest_framework import routers

from core.views import HomeView, ClienteDetalleView, ClienteModificarView, ClienteAgregarView, ClienteListView, \
    UsuarioListView, ClienteEliminarView, DistritoViewSet, LocalidadViewSet


router = routers.DefaultRouter()
router.register(r'distrito', DistritoViewSet)
router.register(r'localidad', LocalidadViewSet)

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('facturacion_clientes.urls'))
    path('accounts/', include('django.contrib.auth.urls')),
    path('', HomeView.as_view(), name='home'),

    path(r'api/', include(router.urls)),

    path('cliente/', ClienteListView.as_view(), name='cliente-listado'),
    path('cliente/<int:pk>/', ClienteDetalleView.as_view(), name='cliente-detalle'),
    path('cliente/<int:pk>/editar/', ClienteModificarView.as_view(), name='cliente-modificar'),
    path('cliente/<int:pk>/eliminar/', ClienteEliminarView.as_view(), name='cliente-eliminar'),
    path('cliente/agregar/', ClienteAgregarView.as_view(), name='cliente-agregar'),

    path('usuarios/', UsuarioListView.as_view(), name='usuario-list')
]
