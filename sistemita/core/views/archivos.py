"""Vistas del modelo Archivo."""

# Django REST framework
from rest_framework import mixins, permissions, viewsets

# Sistemita
from sistemita.core.models.archivo import Archivo
from sistemita.core.serializers import ArchivoSerializer


class ArchivoViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Archivo view set."""

    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = (permissions.IsAuthenticated,)
