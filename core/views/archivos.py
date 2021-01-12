"""Vistas del modelo Archivo."""

# Django REST framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.archivo import Archivo

# Serializers
from core.serializers import ArchivoSerializer


class ArchivoViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Archivo view set."""

    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = (permissions.IsAuthenticated,)
