"""Viewset de medios de pago."""

# Django REST Framework
from rest_framework import mixins, permissions, viewsets

# Sistemita
from sistemita.api.mediopago.serializers import MedioPagoSerializer
from sistemita.core.models.mediopago import MedioPago


class MedioPagoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Medio de pago view set."""

    queryset = MedioPago.objects.all()
    serializer_class = MedioPagoSerializer
    permission_classes = (permissions.IsAuthenticated,)
