"""Vistas del modelo Distrito."""

# Django REST framework
from rest_framework import permissions, viewsets

# Sistemita
from sistemita.core.models.entidad import Distrito
from sistemita.core.serializers import DistritoSerializer


class DistritoViewSet(viewsets.ModelViewSet):
    """Distrito view set."""

    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('provincia',)
