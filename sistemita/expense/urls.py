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
    FondoDetailView,
    FondoListView,
)

urlpatterns = [
    path('fondo/', FondoListView.as_view(), name='fondo-list'),
    path('fondo/<int:pk>/', FondoDetailView.as_view(), name='fondo-detail'),
    path('costo/', CostoListView.as_view(), name='costo-list'),
    path('costo/agregar/', CostoCreateView.as_view(), name='costo-create'),
    path('costo/<int:pk>/', CostoDetailView.as_view(), name='costo-detail'),
    path('costo/<int:pk>/editar/', CostoUpdateView.as_view(), name='costo-update'),
    path('costo/<int:pk>/eliminar/', CostoDeleteView.as_view(), name='costo-delete'),
]
