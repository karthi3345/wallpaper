"""
Seed Self Adhesive Wallpaper products matching the reference site exactly.
Products, names, SKUs, prices, and image URLs from:
redandwinedecor.in/product-category/self-adhesive-wallpaper/

Run: python3 manage.py seed_self_adhesive
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# Exact products from reference site
# (name, sku, image_filename)
SELF_ADHESIVE_PRODUCTS = [
    ('3D Tree Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6880-3',
     'wall-sticker-3-1000x1000-1.webp'),
    ('Floral Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6818-1',
     '09-1.jpg'),
    ('Floral Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6818-4',
     '07-1.jpg'),
    ('Floral Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6819-2',
     '02-1.jpg'),
    ('Floral Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6821-2',
     '10-2.jpg'),
    ('Floral Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6821-3',
     '04-1.jpg'),
    ('Louvers Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6526-2',
     '05-1.jpg'),
    ('Louvers Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6526-3',
     'WhatsApp-Image-2024-11-22-at-18.56.28_cadedd8a.jpg'),
    ('Wooden Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6501-1',
     '03.jpg'),
    ('Wooden Self Adhesive Wallpaper Pack of 2 rolls', 'ZH6511-1',
     '11-1.jpg'),
]

DESCRIPTION = (
    'Self-adhesive wallpaper in a convenient pack of 2 rolls. '
    'Easy peel-and-stick installation — no glue or paste required. '
    'Simply cut to size, peel the backing, and apply to any clean, '
    'smooth surface. Ideal for DIY home makeovers: living rooms, '
    'bedrooms, kitchens, bathrooms, cabinets, and furniture. '
    'Waterproof, removable, and repositionable. Each roll measures '
    '60cm x 2.5m, covering approximately 3 sq ft per roll.'
)


class Command(BaseCommand):
    help = 'Seed Self Adhesive Wallpaper products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Self Adhesive Wallpaper products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='self-adhesive-wallpaper',
                defaults={
                    'name': 'Self Adhesive Wallpaper',
                    'image': IMG_BASE + 'wall-sticker-3-1000x1000-1.webp',
                    'sort_order': 5,
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
            for idx, (name, sku, img_file) in enumerate(SELF_ADHESIVE_PRODUCTS):
                full_name = f'{name} \u2013 {sku}'
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
                    short_description=f'Self adhesive wallpaper \u2014 {sku}',
                    price=Decimal('299'),
                    compare_at_price=None,
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
            f'Seeded {product_count} Self Adhesive Wallpaper products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
