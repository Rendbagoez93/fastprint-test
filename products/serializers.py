from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from products.models import Kategori, Status, Produk


class KategoriSerializer(serializers.ModelSerializer):
    """
    Serializer for Kategori model.
    Handles normalization of external API kategori data.
    """
    
    class Meta:
        model = Kategori
        fields = ['id_kategori', 'nama_kategori']
        read_only_fields = ['id_kategori']
    
    def validate_nama_kategori(self, value):
        """Ensure nama_kategori is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nama kategori tidak boleh kosong.")
        return value.strip()


class StatusSerializer(serializers.ModelSerializer):
    """
    Serializer for Status model.
    Handles normalization of external API status data.
    """
    
    class Meta:
        model = Status
        fields = ['id_status', 'nama_status']
        read_only_fields = ['id_status']
    
    def validate_nama_status(self, value):
        """Ensure nama_status is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nama status tidak boleh kosong.")
        return value.strip()


class ProdukSerializer(serializers.ModelSerializer):
    """
    Serializer for Produk model.
    Handles normalization of external API product data.
    """
    
    # Nested serializers for read operations
    kategori_detail = KategoriSerializer(source='kategori', read_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    
    # Foreign key IDs for write operations
    kategori_id = serializers.IntegerField(write_only=True)
    status_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Produk
        fields = [
            'id_produk',
            'nama_produk',
            'harga',
            'kategori_id',
            'status_id',
            'kategori_detail',
            'status_detail'
        ]
        read_only_fields = ['id_produk', 'kategori_detail', 'status_detail']
    
    def validate_nama_produk(self, value):
        """Ensure nama_produk is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nama produk tidak boleh kosong.")
        return value.strip()
    
    def validate_harga(self, value):
        """Ensure harga is positive."""
        if value < 0:
            raise serializers.ValidationError("Harga harus berupa angka positif.")
        return value
    
    def validate_kategori_id(self, value):
        """Validate that kategori exists."""
        try:
            Kategori.objects.get(id_kategori=value)
        except Kategori.DoesNotExist:
            raise serializers.ValidationError(f"Kategori dengan ID {value} tidak ditemukan.")
        return value
    
    def validate_status_id(self, value):
        """Validate that status exists."""
        try:
            Status.objects.get(id_status=value)
        except Status.DoesNotExist:
            raise serializers.ValidationError(f"Status dengan ID {value} tidak ditemukan.")
        return value
    
    def create(self, validated_data):
        """Create Produk instance with foreign key references."""
        kategori = Kategori.objects.get(id_kategori=validated_data.pop('kategori_id'))
        status = Status.objects.get(id_status=validated_data.pop('status_id'))
        
        return Produk.objects.create(
            kategori=kategori,
            status=status,
            **validated_data
        )
    
    def update(self, instance, validated_data):
        """Update Produk instance with foreign key references."""
        if 'kategori_id' in validated_data:
            kategori = Kategori.objects.get(id_kategori=validated_data.pop('kategori_id'))
            instance.kategori = kategori
        
        if 'status_id' in validated_data:
            status = Status.objects.get(id_status=validated_data.pop('status_id'))
            instance.status = status
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ExternalAPIDataSerializer(serializers.Serializer):
    """
    Serializer for normalizing external API response data.
    Transforms external API format to internal format.
    """
    
    kategori = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    status = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    produk = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    def validate_kategori(self, value):
        """Validate and normalize kategori list."""
        normalized = []
        for item in value:
            if 'id_kategori' in item and 'nama_kategori' in item:
                normalized.append({
                    'id_kategori': int(item['id_kategori']),
                    'nama_kategori': str(item['nama_kategori']).strip()
                })
        return normalized
    
    def validate_status(self, value):
        """Validate and normalize status list."""
        normalized = []
        for item in value:
            if 'id_status' in item and 'nama_status' in item:
                normalized.append({
                    'id_status': int(item['id_status']),
                    'nama_status': str(item['nama_status']).strip()
                })
        return normalized
    
    def validate_produk(self, value):
        """Validate and normalize produk list."""
        normalized = []
        for item in value:
            try:
                # Ensure all required fields are present
                if not all(key in item for key in ['id_produk', 'nama_produk', 'harga', 'kategori_id', 'status_id']):
                    continue
                
                # Normalize harga to Decimal
                try:
                    harga = Decimal(str(item['harga']))
                    if harga < 0:
                        continue
                except (InvalidOperation, ValueError):
                    continue
                
                normalized.append({
                    'id_produk': int(item['id_produk']),
                    'nama_produk': str(item['nama_produk']).strip(),
                    'harga': harga,
                    'kategori_id': int(item['kategori_id']),
                    'status_id': int(item['status_id'])
                })
            except (KeyError, ValueError, TypeError):
                # Skip invalid items
                continue
        
        return normalized
    
    def to_internal_value(self, data):
        """Transform external API data to internal format."""
        if not isinstance(data, dict):
            raise serializers.ValidationError("Data harus berupa dictionary.")
        
        return super().to_internal_value(data)


class ProdukListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing products.
    Includes basic kategori and status information.
    """
    
    kategori_nama = serializers.CharField(source='kategori.nama_kategori', read_only=True)
    status_nama = serializers.CharField(source='status.nama_status', read_only=True)
    
    class Meta:
        model = Produk
        fields = [
            'id_produk',
            'nama_produk',
            'harga',
            'kategori_nama',
            'status_nama'
        ]
