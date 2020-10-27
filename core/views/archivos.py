from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from core.models import Archivo

from core.serializers import ArchivoSerializer


class ArchivoViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = (permissions.IsAuthenticated,)
