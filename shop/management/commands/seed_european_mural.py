"""
Seed European Wall Mural products matching the reference site exactly.
Products from: redandwinedecor.in/product-category/customize-wallpaper/wall/

All 11 products at ₹85/sqft.
None appear on the homepage (featured/best_seller/is_latest = False).

Run: python3 manage.py seed_european_mural
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# (name, image_filename) — all at ₹85/sqft
EUROPEAN_PRODUCTS = [
    ('French historical green I Custom Wallpaper', 'Untitled-42.1.jpg'),
    ('Imperial Bleu Floral Bird Mural \u2013 Luxury Custom Wallpaper', 'ss.png'),
    ('Imperial Riviera Mural \u2013 Customize Wallpaper',
     'WhatsApp-Image-2026-02-15-at-12.00.17-PM.jpeg'),
    ('Majestic Horizon 2- Sketched art I Custom Wallpaper',
     'sletch-moukup-dark-shade.jpg'),
    ('Majestic Horizon- Sketched art I Custom Wallpaper',
     'WhatsApp-Image-2025-08-18-at-1.12.33-PM.jpeg'),
    ('Majestic Palatial Escape I Mural Wallpaper', 'Untitled-48-copy2.jpg'),
    ('Neo-Classical Mythic I Mural Wallpaper', 'Untitled-49.2-copy.jpg'),
    ('Parisian Evening Stroll: Romantic Paris Streetscape Wallpaper Mural',
     'WhatsApp-Image-2025-09-19-at-4.33.00-PM.jpeg'),
    ('Roman Garden- Customize Wallcoverings', 'DESIGNE-28.jpg'),
    ('Royale Equestrian Classical Wall Mural', '0001.jpeg'),
    ('Victorian Garden Retreat\u201d Custom Wallpaper Mural',
     'Gemini_Generated_Image_redi3redi3redi3r.png'),
]

DESCRIPTION = (
    'Premium custom European-style wall mural, hand-crafted to transform '
    'your space. Made to order with high-quality materials for a luxurious '
    'finish. Priced per square foot.'
)


class Command(BaseCommand):
    help = 'Seed European Wall Mural products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding European Wall Mural products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='wall-murals-european',
                defaults={
                    'name': 'European',
                    'image': IMG_BASE + 'Untitled-42.1.jpg',
                    'sort_order': 10,
                    'is_active': True,
                }
            )
            if not created:
                cat.name = 'European'
                cat.image = IMG_BASE + 'Untitled-42.1.jpg'
                cat.is_active = True
                cat.save()

            self.stdout.write(
                f'Category: {cat.name} ({"created" if created else "updated"})'
            )

            old_count = Product.objects.filter(category=cat).count()
            Product.objects.filter(category=cat).delete()
            self.stdout.write(f'Removed {old_count} old products from {cat.name}')

            all_rooms = list(Room.objects.all())
            all_colors = list(Color.objects.all())

            product_count = 0
            for idx, (name, img_file) in enumerate(EUROPEAN_PRODUCTS):
                img_url = IMG_BASE + img_file

                slug = slugify(name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=name,
                    slug=slug,
                    sku=f'EUR-{idx + 1:03d}',
                    description=DESCRIPTION,
                    short_description=name,
                    price=Decimal('85'),
                    compare_at_price=None,
                    unit='sqft',
                    images=[img_url],
                    featured=False,
                    best_seller=False,
                    is_latest=False,
                    status='active',
                    sort_order=idx,
                )
                if all_rooms:
                    product.rooms.set(random.sample(all_rooms, min(2, len(all_rooms))))
                if all_colors:
                    product.colors.set(random.sample(all_colors, min(1, len(all_colors))))
                product_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {product_count} European Wall Mural products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
