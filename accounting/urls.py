"""Accounting URLs modulo"""

# Django
from django.urls import path

# Views
from accounting.views.cobranzas import (
    CobranzaListView, CobranzaAgregarTemplateView
)

urlpatterns = [
    # Cobranza cliente
    path('cobranza/', CobranzaListView.as_view(), name='cobranza-listado'),
    path('cobranza/agregar', CobranzaAgregarTemplateView.as_view(), name='cobranza-agregar'),
]
