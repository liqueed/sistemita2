"""Viewsets de entidades."""

# Django REST framework
from rest_framework import permissions, viewsets

# Sistemita
from sistemita.api.entidades.serializers import (
    DistritoSerializer,
    LocalidadSerializer,
)
from sistemita.core.models.entidad import Distrito, Localidad


class DistritoViewSet(viewsets.ModelViewSet):
    """Distrito view set."""

    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('provincia',)


class LocalidadViewSet(viewsets.ModelViewSet):
    """Localidad view set."""

    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('distrito',)
