from rest_framework import serializers
from products.models import Kategori, Status, Produk


class KategoriSerializer(serializers.ModelSerializer):
    """Serializer for Kategori model."""
    
    class Meta:
        model = Kategori
        fields = ['id_kategori', 'nama_kategori']
        read_only_fields = ['id_kategori']


class StatusSerializer(serializers.ModelSerializer):
    """Serializer for Status model."""
    
    class Meta:
        model = Status
        fields = ['id_status', 'nama_status']
        read_only_fields = ['id_status']


class ProdukSerializer(serializers.ModelSerializer):
    """Serializer for Produk model with nested relationships."""
    
    kategori_detail = KategoriSerializer(source='kategori', read_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    
    class Meta:
        model = Produk
        fields = [
            'id_produk',
            'nama_produk',
            'harga',
            'kategori',
            'status',
            'kategori_detail',
            'status_detail'
        ]
        read_only_fields = ['id_produk', 'kategori_detail', 'status_detail']
        extra_kwargs = {
            'kategori': {'write_only': True},
            'status': {'write_only': True}
        }



