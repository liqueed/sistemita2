from django.urls import path
from . import views

urlpatterns = [
    path('importar_resumen_bancario/', views.importar_resumen_bancario),
]