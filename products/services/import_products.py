from django.db import transaction
from typing import Dict, List, Any, Tuple
from decimal import Decimal, InvalidOperation

from products.models import Kategori, Status, Produk
from products.services.api_client import FastprintAPIClient


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
        # Fetch data from API
        api_data = self.api_client.fetch_data()
        
        if api_data is None:
            return ImportResult(
                success=False,
                message="Failed to fetch data from API"
            )
        
        # Import data into database
        return self.import_data(api_data)
    
    def import_data(self, data: Dict[str, Any]) -> ImportResult:
        # Validate data structure
        validation_result = self._validate_data(data)
        if not validation_result[0]:
            return ImportResult(success=False, message=validation_result[1])
        
        stats = {
            'kategori_created': 0,
            'status_created': 0,
            'produk_created': 0,
            'kategori_skipped': 0,
            'status_skipped': 0,
            'produk_skipped': 0
        }
        
        try:
            # Use atomic transaction - all or nothing
            with transaction.atomic():
                # Import Kategori first (referenced by Produk)
                kategori_stats = self._import_kategori(data.get('kategori', []))
                stats['kategori_created'] = kategori_stats['created']
                stats['kategori_skipped'] = kategori_stats['skipped']
                
                # Import Status (referenced by Produk)
                status_stats = self._import_status(data.get('status', []))
                stats['status_created'] = status_stats['created']
                stats['status_skipped'] = status_stats['skipped']
                
                # Import Produk last (depends on Kategori and Status)
                produk_stats = self._import_produk(data.get('produk', []))
                stats['produk_created'] = produk_stats['created']
                stats['produk_skipped'] = produk_stats['skipped']
            
            total_created = (stats['kategori_created'] + 
                           stats['status_created'] + 
                           stats['produk_created'])
            
            message = (f"Import successful. Created: {total_created} records "
                      f"(Kategori: {stats['kategori_created']}, "
                      f"Status: {stats['status_created']}, "
                      f"Produk: {stats['produk_created']})")
            
            return ImportResult(success=True, message=message, stats=stats)
            
        except Exception as e:
            return ImportResult(
                success=False,
                message=f"Import failed: {str(e)}",
                stats=stats
            )
    
    def _validate_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the structure of API data.
        
        Args:
            data: Dictionary to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        required_keys = ['kategori', 'status', 'produk']
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: '{key}'"
            if not isinstance(data[key], list):
                return False, f"'{key}' must be a list"
        
        return True, ""
    
    def _import_kategori(self, kategori_list: List[Dict]) -> Dict[str, int]:
        """
        Import kategori data with duplicate prevention.
        
        Args:
            kategori_list: List of kategori dictionaries
        
        Returns:
            Dictionary with 'created' and 'skipped' counts
        """
        created = 0
        skipped = 0
        
        for item in kategori_list:
            id_kategori = item.get('id_kategori')
            nama_kategori = item.get('nama_kategori')
            
            if not id_kategori or not nama_kategori:
                continue
            
            # Check for duplicates - idempotent behavior
            if Kategori.objects.filter(id_kategori=id_kategori).exists():
                skipped += 1
                continue
            
            Kategori.objects.create(
                id_kategori=id_kategori,
                nama_kategori=nama_kategori
            )
            created += 1
        
        return {'created': created, 'skipped': skipped}
    
    def _import_status(self, status_list: List[Dict]) -> Dict[str, int]:
        """
        Import status data with duplicate prevention.
        
        Args:
            status_list: List of status dictionaries
        
        Returns:
            Dictionary with 'created' and 'skipped' counts
        """
        created = 0
        skipped = 0
        
        for item in status_list:
            id_status = item.get('id_status')
            nama_status = item.get('nama_status')
            
            if not id_status or not nama_status:
                continue
            
            # Check for duplicates - idempotent behavior
            if Status.objects.filter(id_status=id_status).exists():
                skipped += 1
                continue
            
            Status.objects.create(
                id_status=id_status,
                nama_status=nama_status
            )
            created += 1
        
        return {'created': created, 'skipped': skipped}
    
    def _import_produk(self, produk_list: List[Dict]) -> Dict[str, int]:
        """
        Import produk data with duplicate prevention and foreign key validation.
        
        Args:
            produk_list: List of produk dictionaries
        
        Returns:
            Dictionary with 'created' and 'skipped' counts
        """
        created = 0
        skipped = 0
        
        for item in produk_list:
            id_produk = item.get('id_produk')
            nama_produk = item.get('nama_produk')
            harga = item.get('harga')
            kategori_id = item.get('kategori_id')
            status_id = item.get('status_id')
            
            # Validate required fields
            if not all([id_produk, nama_produk, harga, kategori_id, status_id]):
                continue
            
            # Check for duplicates - idempotent behavior
            if Produk.objects.filter(id_produk=id_produk).exists():
                skipped += 1
                continue
            
            # Validate and convert harga to Decimal
            try:
                harga_decimal = Decimal(str(harga))
            except (InvalidOperation, ValueError):
                continue
            
            # Validate foreign keys exist
            try:
                kategori = Kategori.objects.get(id_kategori=kategori_id)
                status = Status.objects.get(id_status=status_id)
            except (Kategori.DoesNotExist, Status.DoesNotExist):
                # Skip if referenced kategori or status doesn't exist
                continue
            
            Produk.objects.create(
                id_produk=id_produk,
                nama_produk=nama_produk,
                harga=harga_decimal,
                kategori=kategori,
                status=status
            )
            created += 1
        
        return {'created': created, 'skipped': skipped}


def import_products_from_api() -> ImportResult:
    service = ProductImportService()
    return service.fetch_and_import()
