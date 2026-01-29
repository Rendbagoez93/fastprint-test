from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Kategori(models.Model):
    id_kategori = models.AutoField(primary_key=True)
    nama_kategori = models.CharField(max_length=100)

    class Meta:
        db_table = 'kategori'
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategori'
        ordering = ['nama_kategori']

    def clean(self):
        if not self.nama_kategori or not self.nama_kategori.strip():
            raise ValidationError({'nama_kategori': 'Nama kategori tidak boleh kosong.'})
        self.nama_kategori = self.nama_kategori.strip()

    def __str__(self):
        return self.nama_kategori


class Status(models.Model):
    id_status = models.AutoField(primary_key=True)
    nama_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'status'
        verbose_name = 'Status'
        verbose_name_plural = 'Status'
        ordering = ['nama_status']

    def clean(self):
        if not self.nama_status or not self.nama_status.strip():
            raise ValidationError({'nama_status': 'Nama status tidak boleh kosong.'})
        self.nama_status = self.nama_status.strip()

    def __str__(self):
        return self.nama_status


class Produk(models.Model):
    id_produk = models.AutoField(primary_key=True)
    nama_produk = models.CharField(max_length=200)
    harga = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    kategori = models.ForeignKey(
        Kategori,
        on_delete=models.CASCADE,
        db_column='kategori_id',
        related_name='produk_set'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        db_column='status_id',
        related_name='produk_set'
    )

    class Meta:
        db_table = 'produk'
        verbose_name = 'Produk'
        verbose_name_plural = 'Produk'
        ordering = ['-id_produk']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['kategori']),
        ]

    def clean(self):
        if not self.nama_produk or not self.nama_produk.strip():
            raise ValidationError({'nama_produk': 'Nama produk tidak boleh kosong.'})
        self.nama_produk = self.nama_produk.strip()
        
        if self.harga is not None and self.harga < 0:
            raise ValidationError({'harga': 'Harga harus berupa angka positif.'})

    def __str__(self):
        return self.nama_produk
