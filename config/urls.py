"""URLs de sistemita."""

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    # path('admin/', admin.site.urls),
    # API
    path('api/', include('sistemita.api.urls')),
    # Account
    path('accounts/', include('django.contrib.auth.urls')),
    # Core
    path('', include('sistemita.core.urls', namespace='core')),
    # Accounting module
    path('', include('sistemita.accounting.urls', namespace='accounting')),
    # Auth module
    path('', include('sistemita.authorization.urls', namespace='authentication')),
    # Expense module
    path('', include('sistemita.expense.urls', namespace='expense')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
