"""Accounting URLs modulo"""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework import routers

# Views
from accounting.views.cobranzas import (
    CobranzaViewSet, CobranzaListView, CobranzaAgregarTemplateView,
    CobranzaEditarTemplateView
)

router = routers.DefaultRouter()
router.register(r'cobranza', CobranzaViewSet)

urlpatterns = [
    # API
    path(r'api/', include(router.urls)),

    # Cobranza cliente
    path('cobranza/', CobranzaListView.as_view(), name='cobranza-listado'),
    path('cobranza/agregar', CobranzaAgregarTemplateView.as_view(), name='cobranza-agregar'),
    path('cobranza/<int:pk>/editar/', CobranzaEditarTemplateView.as_view(), name='cobranza-modificar'),
]
