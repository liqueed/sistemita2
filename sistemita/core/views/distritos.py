"""Vistas del modelo Distrito."""

# Django REST framework
from rest_framework import permissions
from rest_framework import viewsets

# Models
from core.models.entidad import Distrito

# Serializers
from core.serializers import DistritoSerializer


class DistritoViewSet(viewsets.ModelViewSet):
    """Distrito view set."""

    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('provincia',)
