import os
from django.conf import settings
from django.core.management.base import BaseCommand
from catalog.models import Product, Category


class Command(BaseCommand):
    help = 'Add test products'

    def handle(self, *args, **options):
        images_dir = os.path.join(settings.BASE_DIR, 'media', 'photos')
        category, _ = Category.objects.get_or_create(category_name='Продукты для губ', description='Уходовая и декоративная косметика для губ.')

        products = [
            {'product_name': 'Блеск для губ', 'description': 'Love Generation', 'image': os.path.join(images_dir, 'lipgloss.png'), 'category': category, 'price': 347, 'created_at': '2025-09-05', 'updated_at': '2025-09-05'},
            {'product_name': 'Карандаш для губ', 'description': 'Love Generation', 'image': os.path.join(images_dir, 'lip_product.png'), 'category': category, 'price': 198, 'created_at': '2025-09-05', 'updated_at': '2025-09-05'}
        ]

        for test_product in products:
            product, created = Product.objects.get_or_create(**test_product)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added product: {product.product_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'This product already exists: {product.product_name}'))