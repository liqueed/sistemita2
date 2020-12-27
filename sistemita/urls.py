"""URLs de sistemita."""

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include,  path

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('facturacion_clientes.urls'))

    # Account
    path('accounts/', include('django.contrib.auth.urls')),

    # Core
    path('', include(('core.urls', 'core'), namespace='core')),

    # Accounting module
    path('', include(('accounting.urls', 'accounting'), namespace='accounting')),

    # Auth module
    path('', include(('authorization.urls', 'authorization'), namespace='authentication')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
