"""View set Factura."""

# Django REST Framework
from rest_framework import mixins, permissions, viewsets

from sistemita.core.models.cliente import Factura
from sistemita.core.serializers import FacturaSerializer


class FacturaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura view set."""

    filter_fields = ('cliente', 'cobrado')
    queryset = Factura.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FacturaSerializer
