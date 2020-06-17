from django.urls import path, include

from core.views import HomeView, ClienteListView, UsuarioListView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('facturacion_clientes.urls'))
    path('accounts/', include('django.contrib.auth.urls')),
    path('', HomeView.as_view(), name='home'),

    path('clientes/', ClienteListView.as_view(), name='cliente-list'),

    path('usuarios/', UsuarioListView.as_view(), name='usuario-list')
]
