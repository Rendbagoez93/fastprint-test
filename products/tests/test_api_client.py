"""
Test the API client
"""

import sys
import os
import django

from products.services.api_client import FastprintAPIClient
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()



if __name__ == "__main__":
    print("="*70)
    print("TESTING UPDATED API CLIENT")
    print("="*70)
    
    client = FastprintAPIClient()
    
    credentials = client.get_credentials()
    print(f"\nGenerated Credentials:")
    print(f"  Username: {credentials['username']}")
    print(f"  Password: {credentials['password']}")
    
    print(f"\n{'='*70}")
    print("FETCHING DATA FROM API...")
    print(f"{'='*70}\n")
    
    data = client.fetch_data()
    
    if data:
        print("✅ SUCCESS! API returned data\n")
        print(f"Response Keys: {list(data.keys())}")
        
        if 'error' in data:
            print(f"Error Code: {data['error']}")
        
        if 'version' in data:
            print(f"API Version: {data['version']}")
        
        if 'data' in data:
            products = data['data']
            print(f"\nTotal Products: {len(products)}")
            
            if len(products) > 0:
                print(f"\nFirst 3 Products:")
                for i, product in enumerate(products[:3], 1):
                    print(f"\n  {i}. {product.get('nama_produk', 'N/A')}")
                    print(f"     ID: {product.get('id_produk', 'N/A')}")
                    print(f"     Kategori: {product.get('kategori', 'N/A')}")
                    print(f"     Harga: Rp {product.get('harga', 'N/A')}")
                    print(f"     Status: {product.get('status', 'N/A')}")
        
        print(f"\n{'='*70}")
        print("✅ API CLIENT WORKING CORRECTLY!")
        print(f"{'='*70}")
    else:
        print("❌ FAILED! API did not return data")
        print(f"{'='*70}")
