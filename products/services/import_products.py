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
        """
        Fetch data from API and import into database.
        
        Returns:
            ImportResult with success status, message, and statistics
        """
        # Fetch data from API
        api_data = self.api_client.fetch_data()
        
        if api_data is None:
            return ImportResult(
                success=False,
                message="Failed to fetch data from API"
            )
        
        # Check for API errors
        if isinstance(api_data, dict) and api_data.get('error') == 1:
            return ImportResult(
                success=False,
                message=f"API Error: {api_data.get('ket', 'Unknown error')}"
            )
        
        # Transform API response to expected format
        transformed_data = self._transform_api_response(api_data)
        
        # Import data into database
        return self.import_data(transformed_data)
    
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
    
    def _transform_api_response(self, api_data: Dict[str, Any]) -> Dict[str, List]:
        """
        Transform API response from flat structure to normalized structure.
        
        API returns:
        {
            "error": 0,
            "version": "...",
            "data": [
                {
                    "id_produk": "6",
                    "nama_produk": "...",
                    "kategori": "L QUEENLY",
                    "harga": "12500",
                    "status": "bisa dijual"
                }
            ]
        }
        
        Transform to:
        {
            "kategori": [{"id_kategori": 1, "nama_kategori": "L QUEENLY"}],
            "status": [{"id_status": 1, "nama_status": "bisa dijual"}],
            "produk": [{"id_produk": 6, "nama_produk": "...", "kategori_id": 1, "status_id": 1, "harga": 12500}]
        }
        """
        products_data = api_data.get('data', [])
        
        # Extract unique categories and statuses
        kategori_map = {}  # {nama_kategori: id_kategori}
        status_map = {}    # {nama_status: id_status}
        
        kategori_id_counter = 1
        status_id_counter = 1
        
        for product in products_data:
            # Extract kategori
            kategori_name = product.get('kategori', '').strip()
            if kategori_name and kategori_name not in kategori_map:
                kategori_map[kategori_name] = kategori_id_counter
                kategori_id_counter += 1
            
            # Extract status
            status_name = product.get('status', '').strip()
            if status_name and status_name not in status_map:
                status_map[status_name] = status_id_counter
                status_id_counter += 1
        
        # Build kategori list
        kategori_list = [
            {'id_kategori': id_kat, 'nama_kategori': nama_kat}
            for nama_kat, id_kat in kategori_map.items()
        ]
        
        # Build status list
        status_list = [
            {'id_status': id_stat, 'nama_status': nama_stat}
            for nama_stat, id_stat in status_map.items()
        ]
        
        # Build produk list with foreign key references
        produk_list = []
        for product in products_data:
            try:
                kategori_name = product.get('kategori', '').strip()
                status_name = product.get('status', '').strip()
                
                if not kategori_name or not status_name:
                    continue
                
                produk_list.append({
                    'id_produk': int(product.get('id_produk', 0)),
                    'nama_produk': product.get('nama_produk', '').strip(),
                    'harga': product.get('harga', '0'),
                    'kategori_id': kategori_map[kategori_name],
                    'status_id': status_map[status_name]
                })
            except (ValueError, KeyError):
                continue
        
        return {
            'kategori': kategori_list,
            'status': status_list,
            'produk': produk_list
        }
    
    def _validate_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
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
