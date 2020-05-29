from django.urls import path, include

from core.views import HomeView, ClienteListView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('facturacion_clientes.urls'))
    path('accounts/', include('django.contrib.auth.urls')),
    path('', HomeView.as_view(), name='home'),
    path('cliente/', ClienteListView.as_view(), name='cliente-list')
]
