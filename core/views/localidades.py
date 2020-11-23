from rest_framework import permissions
from rest_framework import viewsets

from core.models.entidad import Localidad
from core.serializers import LocalidadSerializer


class LocalidadViewSet(viewsets.ModelViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('distrito',)
