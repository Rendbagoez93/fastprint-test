from django.db import transaction
from typing import Dict, List, Any
from decimal import Decimal, InvalidOperation
import logging

from products.models import Kategori, Status, Produk
from products.services.api_client import FastprintAPIClient

logger = logging.getLogger('products')


class ImportResult:
    """Data class to hold import operation results."""
    
    def __init__(self, success: bool, message: str, stats: Dict[str, int] = None):
        self.success = success
        self.message = message
        self.stats = stats or {
            'kategori_created': 0,
            'status_created': 0,
            'produk_created': 0,
            'kategori_skipped': 0,
            'status_skipped': 0,
            'produk_skipped': 0
        }
    
    def __repr__(self):
        return f"ImportResult(success={self.success}, message='{self.message}', stats={self.stats})"


class ProductImportService:
    """Service class for importing products from external API."""
    
    def __init__(self, api_client: FastprintAPIClient = None):
        self.api_client = api_client or FastprintAPIClient()
    
    def fetch_and_import(self) -> ImportResult:
        """
        Fetch data from API and import into database.
        
        Returns:
            ImportResult with success status, message, and statistics
        """
        logger.info("Starting product import from external API")
        
        # Fetch data from API
        api_data = self.api_client.fetch_data()
        
        if api_data is None:
            logger.error("Failed to fetch data from API")
            return ImportResult(
                success=False,
                message="Failed to fetch data from API"
            )
        
        # Check for API errors
        if isinstance(api_data, dict) and api_data.get('error') == 1:
            error_msg = f"API Error: {api_data.get('ket', 'Unknown error')}"
            logger.error(error_msg)
            return ImportResult(
                success=False,
                message=error_msg
            )
        
        logger.info("Successfully fetched data from API")
        
        # Transform API response to expected format
        transformed_data = self._transform_api_response(api_data)
        logger.info(f"Transformed data: {len(transformed_data.get('kategori', []))} categories, "
                   f"{len(transformed_data.get('status', []))} statuses, "
                   f"{len(transformed_data.get('produk', []))} products")
        
        # Import data into database
        result = self.import_data(transformed_data)
        
        if result.success:
            logger.info(f"Import completed successfully: {result.message}")
        else:
            logger.error(f"Import failed: {result.message}")
        
        return result
    
    def import_data(self, data: Dict[str, Any]) -> ImportResult:
        """Import data into database with transaction support."""
        error_msg = self._validate_data(data)
        if error_msg:
            return ImportResult(success=False, message=error_msg)
        
        try:
            with transaction.atomic():
                kat_stats = self._import_model(
                    Kategori, data.get('kategori', []), 
                    'id_kategori', 'nama_kategori'
                )
                stat_stats = self._import_model(
                    Status, data.get('status', []), 
                    'id_status', 'nama_status'
                )
                prod_stats = self._import_produk(data.get('produk', []))
            
            stats = {
                'kategori_created': kat_stats['created'],
                'kategori_skipped': kat_stats['skipped'],
                'status_created': stat_stats['created'],
                'status_skipped': stat_stats['skipped'],
                'produk_created': prod_stats['created'],
                'produk_skipped': prod_stats['skipped']
            }
            
            total_created = sum([s['created'] for s in [kat_stats, stat_stats, prod_stats]])
            message = (
                f"Import successful. Created {total_created} records "
                f"(Kategori: {kat_stats['created']}, "
                f"Status: {stat_stats['created']}, "
                f"Produk: {prod_stats['created']})"
            )
            
            return ImportResult(success=True, message=message, stats=stats)
            
        except Exception as e:
            return ImportResult(success=False, message=f"Import failed: {str(e)}")
    
    def _transform_api_response(self, api_data: Dict[str, Any]) -> Dict[str, List]:
        """Transform API response from flat structure to normalized structure."""
        products_data = api_data.get('data', [])
        kategori_map = {}
        status_map = {}
        
        # Extract unique categories and statuses
        for product in products_data:
            kategori = product.get('kategori', '').strip()
            status = product.get('status', '').strip()
            
            if kategori and kategori not in kategori_map:
                kategori_map[kategori] = len(kategori_map) + 1
            if status and status not in status_map:
                status_map[status] = len(status_map) + 1
        
        # Build normalized lists
        kategori_list = [
            {'id_kategori': id_val, 'nama_kategori': nama} 
            for nama, id_val in kategori_map.items()
        ]
        status_list = [
            {'id_status': id_val, 'nama_status': nama} 
            for nama, id_val in status_map.items()
        ]
        
        # Build product list
        produk_list = []
        for product in products_data:
            kategori = product.get('kategori', '').strip()
            status = product.get('status', '').strip()
            
            if not (kategori and status):
                continue
                
            try:
                produk_list.append({
                    'id_produk': int(product.get('id_produk', 0)),
                    'nama_produk': product.get('nama_produk', '').strip(),
                    'harga': product.get('harga', '0'),
                    'kategori_id': kategori_map[kategori],
                    'status_id': status_map[status]
                })
            except (ValueError, KeyError):
                continue
        
        return {
            'kategori': kategori_list, 
            'status': status_list, 
            'produk': produk_list
        }
    
    def _validate_data(self, data: Dict[str, Any]) -> str:
        """Validate data structure. Returns error message or empty string if valid."""
        if not isinstance(data, dict):
            return "Data must be a dictionary"
        
        for key in ['kategori', 'status', 'produk']:
            if key not in data:
                return f"Missing required key: '{key}'"
            if not isinstance(data[key], list):
                return f"'{key}' must be a list"
        
        return ""
    
    def _import_model(self, model_class, items: List[Dict], 
                     id_field: str, name_field: str) -> Dict[str, int]:
        """Generic import function for simple models (Kategori, Status)."""
        created = skipped = 0
        
        for item in items:
            id_value = item.get(id_field)
            name_value = item.get(name_field)
            
            if not (id_value and name_value):
                skipped += 1
                continue
            
            _, is_created = model_class.objects.get_or_create(
                **{id_field: id_value},
                defaults={name_field: name_value}
            )
            
            if is_created:
                created += 1
            else:
                skipped += 1
        
        return {'created': created, 'skipped': skipped}
    
    def _import_produk(self, produk_list: List[Dict]) -> Dict[str, int]:
        """Import products with foreign key validation."""
        created = skipped = 0
        required_fields = ['id_produk', 'nama_produk', 'harga', 'kategori_id', 'status_id']
        
        for item in produk_list:
            # Validate required fields
            if not all(item.get(f) for f in required_fields):
                skipped += 1
                continue
            
            # Check if product already exists
            if Produk.objects.filter(id_produk=item['id_produk']).exists():
                skipped += 1
                continue
            
            try:
                # Get foreign key instances
                kategori = Kategori.objects.get(id_kategori=item['kategori_id'])
                status = Status.objects.get(id_status=item['status_id'])
                
                # Create product
                Produk.objects.create(
                    id_produk=item['id_produk'],
                    nama_produk=item['nama_produk'],
                    harga=Decimal(str(item['harga'])),
                    kategori=kategori,
                    status=status
                )
                created += 1
            except (InvalidOperation, ValueError, Kategori.DoesNotExist, Status.DoesNotExist):
                skipped += 1
        
        return {'created': created, 'skipped': skipped}


def import_products_from_api() -> ImportResult:
    service = ProductImportService()
    return service.fetch_and_import()
