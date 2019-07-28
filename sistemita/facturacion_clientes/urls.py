from django.urls import path
from . import views

urlpatterns = [
    path('', views.subir_resumen_bancario, name='subir_resumen_bancario'),
]