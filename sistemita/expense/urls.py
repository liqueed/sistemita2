"""URLs Expense."""

# Django
from django.urls import path

# Vistas
from sistemita.expense.views import (
    CostoCreateView,
    CostoListView,
    FondoListView,
)

urlpatterns = [
    path('fondo/', FondoListView.as_view(), name='fondo-list'),
    path('costos/', CostoListView.as_view(), name='costo-list'),
    path('costos/agregar', CostoCreateView.as_view(), name='costo-create'),
]
