from rest_framework import permissions
from rest_framework import viewsets

from core.models.entidad import Distrito
from core.serializers import DistritoSerializer


class DistritoViewSet(viewsets.ModelViewSet):
    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('provincia',)
