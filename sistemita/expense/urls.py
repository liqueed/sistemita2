"""URLs Expense."""

# Django
from django.urls import path

# Vistas
from sistemita.expense.views import (
    CostoCreateView,
    CostoDeleteView,
    CostoDetailView,
    CostoListView,
    CostoUpdateView,
    FondoListView,
)

urlpatterns = [
    path('fondo/', FondoListView.as_view(), name='fondo-list'),
    path('costos/', CostoListView.as_view(), name='costo-list'),
    path('costos/agregar', CostoCreateView.as_view(), name='costo-create'),
    path('costos/<int:pk>/', CostoDetailView.as_view(), name='costo-detail'),
    path('costos/<int:pk>/editar/', CostoUpdateView.as_view(), name='costo-update'),
    path('costos/<int:pk>/eliminar/', CostoDeleteView.as_view(), name='costo-delete'),
]
