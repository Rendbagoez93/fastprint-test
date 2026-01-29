"""API views for products app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from products.models import Kategori, Status, Produk
from products.serializers import KategoriSerializer, StatusSerializer, ProdukSerializer
from products.services.import_products import ProductImportService


class KategoriViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing Kategori."""
    queryset = Kategori.objects.all()
    serializer_class = KategoriSerializer


class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing Status."""
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class ProdukViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Produk with filtering."""
    queryset = Produk.objects.select_related('kategori', 'status')
    serializer_class = ProdukSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['kategori', 'status']
    
    @action(detail=False, methods=['post'])
    def import_from_api(self, request):
        """Import products from external API."""
        service = ProductImportService()
        result = service.fetch_and_import()
        
        if result.success:
            return Response({
                'success': True,
                'message': result.message,
                'stats': result.stats
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result.message
            }, status=status.HTTP_400_BAD_REQUEST)
