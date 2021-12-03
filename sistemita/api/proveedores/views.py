"""Viewset proveedores"""

# Pandas
import pandas as pd

# Django REST Framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from unidecode import unidecode

# Sistemita
from sistemita.api.proveedores.filters import (
    FacturaProveedorFilterSet,
    ProveedorFilterSet,
)
from sistemita.api.proveedores.serializers import (
    FacturaProveedorBeforeImportSerializer,
    FacturaProveedorImportSerializer,
    FacturaProveedorImputadaModelSerializer,
    FacturaProveedorSerializer,
    ProveedorSerializer,
)
from sistemita.core.models.proveedor import (
    FacturaProveedor,
    FacturaProveedorImputada,
    Proveedor,
)


class ProveedorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Proveedor view set."""

    queryset = Proveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProveedorSerializer

    # Filter
    filter_fields = 'razon_social__cuit__icontains'
    filterset_class = ProveedorFilterSet
    filter_backends = (DjangoFilterBackend,)


class FacturaProveedorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura de proveedores view set."""

    queryset = FacturaProveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    # Filters
    filter_fields = ('proveedor', 'cobrado', 'numero__icontains', 'tipo__exclude', 'tipo__startswith')
    filterset_class = FacturaProveedorFilterSet
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Devuelve un serializador en base a una acción."""
        action_mappings = {
            'validate_import': FacturaProveedorBeforeImportSerializer,
            'list_import': FacturaProveedorImportSerializer,
        }
        return action_mappings.get(self.action, FacturaProveedorSerializer)

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
            df = df.fillna('')
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
                            'tipo_doc_emisor': row.get('tipo_doc_emisor', None),
                            'nro_doc_emisor': row.get('nro_doc_emisor', None),
                            'denominacion_emisor': row.get('denominacion_emisor', None),
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


class FacturaProveedorImputadaViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Factura Imputada view set."""

    queryset = FacturaProveedorImputada.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FacturaProveedorImputadaModelSerializer
