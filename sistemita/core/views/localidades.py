"""Vistas del modelo Localidad."""

# Django REST framework
from rest_framework import permissions, viewsets

# Sistemita
from sistemita.core.models.entidad import Localidad
from sistemita.core.serializers import LocalidadSerializer


class LocalidadViewSet(viewsets.ModelViewSet):
    """Localidad view set."""

    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('distrito',)
