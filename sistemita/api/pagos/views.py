"""Viewset pagos."""

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Sistemita
from sistemita.accounting.models.pago import Pago
from sistemita.api.pagos.serializers import (
    CreateUpdatePagoModelSerializer,
    PagoModelSerializer,
)


class PagoViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Pago view set."""

    queryset = Pago.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PagoModelSerializer

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action in ['create', 'update']:
            return CreateUpdatePagoModelSerializer
        return PagoModelSerializer
