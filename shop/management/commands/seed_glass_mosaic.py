"""
Seed Glass Mosaic Tiles products matching the reference site exactly.
Products, names, SKUs, prices, and image URLs from:
redandwinedecor.in/product-category/glass-mosaic-tiles/

Run: python3 manage.py seed_glass_mosaic
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# Exact products from reference site page 1 of 3
# (name, sku, price, compare_at_price, image_filename)
GLASS_MOSAIC_PRODUCTS = [
    ('Mirror Glass Copper Brick Mosaic Tiles Box', 'MR0016', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-4-scaled-1.jpg'),
    ('Mirror Glass Copper Gold Mosaic Tiles Box', 'GL 5037', Decimal('5913'), Decimal('7000'),
     'GLASS-MOSAIC._page-0010.jpg'),
    ('Mirror Glass Copper Gold Mosaic Tiles Box', 'GL 5075', Decimal('5913'), Decimal('7000'),
     'GLASS-MOSAIC-images-14.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'GL 5041', Decimal('5913'), Decimal('7000'),
     'GLASS-MOSAIC._page-0013.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'GL 5047', Decimal('6666'), Decimal('8078'),
     'GLASS-MOSAIC-images-4.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'GL 5050', Decimal('6666'), Decimal('8078'),
     'GLASS-MOSAIC._page-0018.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'MR0004', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-9-scaled-1.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'MR0008', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-14-scaled-1.jpg'),
    ('Mirror Glass Copper Mosaic Tiles Box', 'MR0012', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-18-scaled-1.jpg'),
    ('Mirror Glass Gold Brick Mosaic Tiles Box', 'MR0013', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-3-scaled-1.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box Mirror/Silver', 'MR0003', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-6-scaled-1.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box', 'GL 5035', Decimal('5913'), Decimal('7000'),
     'GLASS-MOSAIC._page-0012.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box', 'GL 5039', Decimal('5913'), Decimal('7000'),
     'GLASS-MOSAIC._page-0014.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box', 'GL 5044', Decimal('6666'), Decimal('8078'),
     'GLASS-MOSAIC-images-1.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box', 'GL 5074', Decimal('5913'), None,
     'GLASS-MOSAIC-images-16.jpg'),
    ('Mirror Glass Gold Mosaic Tiles Box', 'MR0001', Decimal('5913'), Decimal('7000'),
     'Mirror-Glass-Mosaic-PPT-images-8-scaled-1.jpg'),
]

DESCRIPTION = (
    'Premium glass mosaic tiles crafted with precision for a luxurious finish. '
    'Each box covers approximately 10-12 sq ft. Ideal for kitchen backsplashes, '
    'bathroom feature walls, accent walls, and decorative borders. The reflective '
    'glass surface adds depth and light to any space. Easy to install with standard '
    'thinset adhesive. Resistant to water, stains, and fading.'
)


class Command(BaseCommand):
    help = 'Seed Glass Mosaic Tiles products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Glass Mosaic Tiles products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='glass-mosaic-tiles',
                defaults={
                    'name': 'Glass Mosaic Tiles',
                    'image': IMG_BASE + 'Mirror-Glass-Mosaic-PPT-images-4-scaled-1.jpg',
                    'sort_order': 3,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created category: {cat.name}')
            else:
                self.stdout.write(f'Using existing category: {cat.name}')

            old_count = Product.objects.filter(category=cat).count()
            Product.objects.filter(category=cat).delete()
            self.stdout.write(f'Removed {old_count} old products from {cat.name}')

            all_rooms = list(Room.objects.all())
            all_colors = list(Color.objects.all())

            product_count = 0
            for idx, (name, sku, price, compare_at, img_file) in enumerate(GLASS_MOSAIC_PRODUCTS):
                full_name = f'{name}-{sku}'
                img_url = IMG_BASE + img_file

                # Generate unique slug
                slug = slugify(full_name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=full_name,
                    slug=slug,
                    sku=sku,
                    description=DESCRIPTION,
                    short_description=f'Glass mosaic tiles — {sku}',
                    price=price,
                    compare_at_price=compare_at,
                    unit='pc',
                    images=[img_url],
                    featured=False,       # never on homepage
                    best_seller=False,    # never on homepage
                    is_latest=False,      # never on homepage
                    status='active',
                    sort_order=idx,
                )
                if all_rooms:
                    product.rooms.set(random.sample(all_rooms, min(2, len(all_rooms))))
                if all_colors:
                    product.colors.set(random.sample(all_colors, min(1, len(all_colors))))
                product_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {product_count} Glass Mosaic Tiles products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
