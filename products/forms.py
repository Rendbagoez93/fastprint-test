from django import forms
from django.core.exceptions import ValidationError
from products.models import Produk, Kategori, Status


class ProdukForm(forms.ModelForm):
    """
    Form for creating and editing Produk with validation.
    """
    
    class Meta:
        model = Produk
        fields = ['nama_produk', 'harga', 'kategori', 'status']
        labels = {
            'nama_produk': 'Nama Produk',
            'harga': 'Harga',
            'kategori': 'Kategori',
            'status': 'Status',
        }
        widgets = {
            'nama_produk': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama produk',
                'required': True
            }),
            'harga': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan harga',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'kategori': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def clean_nama_produk(self):
        """
        Validate that nama_produk is not empty or just whitespace.
        """
        nama_produk = self.cleaned_data.get('nama_produk')
        
        if not nama_produk or not nama_produk.strip():
            raise ValidationError('Nama produk harus diisi.')
        
        return nama_produk.strip()
    
    def clean_harga(self):
        """
        Validate that harga is a positive number.
        """
        harga = self.cleaned_data.get('harga')
        
        if harga is None:
            raise ValidationError('Harga harus diisi.')
        
        if harga < 0:
            raise ValidationError('Harga harus berupa angka positif.')
        
        return harga