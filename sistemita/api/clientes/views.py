"""Viewset clientes."""

# Pandas
import pandas as pd

# Django REST Framework
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from unidecode import unidecode

# Sistemita
from sistemita.api.clientes.serializers import (
    ClienteSerializer,
    FacturaBeforeImportSerializer,
    FacturaImportSerializer,
    FacturaSerializer,
)
from sistemita.core.models.cliente import Cliente, Factura


class ClienteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Cliente View set."""

    queryset = Cliente.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClienteSerializer


class FacturaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura view set."""

    filter_fields = ('cliente', 'cobrado')
    queryset = Factura.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        """Devuelve un serializador en base a una acción."""
        action_mappings = {
            'validate_import': FacturaBeforeImportSerializer,
            'list_import': FacturaImportSerializer,
        }
        return action_mappings.get(self.action, FacturaSerializer)

    @action(detail=False, methods=['post'], url_path='validar-importacion')
    def validate_import(self, request):
        """Valida datos a importar."""
        file = request.FILES.get('file')
        errors = []
        result = []
        result_status = None
        if not file:
            result.append({'message': 'error'})

        try:
            df = pd.read_excel(file)
            df.columns = map(lambda header: unidecode(header.replace(" ", "_").replace(".", "").lower()), df.columns)
            data = df.to_dict(orient='records')
            serializer_class = self.get_serializer_class()

            for row in data:
                serializer = serializer_class(data=row)
                if not serializer.is_valid():
                    errors.append(
                        {
                            'fecha': row.get('fecha', None),
                            'tipo': row.get('tipo', None),
                            'punto_de_venta': row.get('punto_de_venta', None),
                            'numero_desde': row.get('numero_desde', None),
                            'tipo_doc_receptor': row.get('tipo_doc_receptor', None),
                            'nro_doc_receptor': row.get('nro_doc_receptor', None),
                            'denominacion_receptor': row.get('denominacion_receptor', None),
                            'moneda': row.get('moneda', None),
                            'imp_neto_gravado': row.get('imp_neto_gravado', None),
                            'imp_total': row.get('imp_total', None),
                            'errors': serializer.errors,
                        }
                    )
                else:
                    result.append(serializer.data)
            result_status = status.HTTP_200_OK
        except Exception as error:
            errors.append(str(error))
            result_status = status.HTTP_400_BAD_REQUEST

        data = {'result': result, 'errors': errors}
        return Response(data, status=result_status)

    @action(detail=False, methods=['post'], url_path='importar-lista')
    def list_import(self, request):
        """Importación de listado facturas de clientes."""
        facturas = request.data.get('facturas', None)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=facturas, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_201_CREATED)
