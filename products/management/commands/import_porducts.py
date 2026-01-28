from django.core.management.base import BaseCommand
from products.services.import_products import ProductImportService


class Command(BaseCommand):
    help = 'Import products, categories, and status from external API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate import without saving to database',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting product import...')
        self.stdout.write('-' * 50)
        
        # Initialize the import service
        service = ProductImportService()
        
        # Fetch and import data
        result = service.fetch_and_import()
        
        # Display results
        self.stdout.write('-' * 50)
        if result.success:
            self.stdout.write(self.style.SUCCESS(f'✓ {result.message}'))
            self.stdout.write('')
            self.stdout.write('Statistics:')
            self.stdout.write(f'  Kategori: {result.stats["kategori_created"]} created, '
                            f'{result.stats["kategori_skipped"]} skipped')
            self.stdout.write(f'  Status:   {result.stats["status_created"]} created, '
                            f'{result.stats["status_skipped"]} skipped')
            self.stdout.write(f'  Produk:   {result.stats["produk_created"]} created, '
                            f'{result.stats["produk_skipped"]} skipped')
        else:
            self.stdout.write(self.style.ERROR(f'✗ {result.message}'))
            return
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
