"""Vistas del modelo Localidad."""

# Django REST framework
from rest_framework import permissions
from rest_framework import viewsets

# Modelos
from core.models.entidad import Localidad

# Serializers
from core.serializers import LocalidadSerializer


class LocalidadViewSet(viewsets.ModelViewSet):
    """Localidad view set."""

    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('distrito',)
