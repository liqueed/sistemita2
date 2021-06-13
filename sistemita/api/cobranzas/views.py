"""Viewset de cobranzas."""

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Sistemita
from sistemita.accounting.models.cobranza import Cobranza
from sistemita.api.cobranzas.serializers import CobranzaSerializer


class CobranzaViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Cobranza view set."""

    queryset = Cobranza.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CobranzaSerializer
