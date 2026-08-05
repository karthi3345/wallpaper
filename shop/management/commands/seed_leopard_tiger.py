"""
Seed Leopard Tiger Wall Mural products matching the reference site exactly.
Products from: redandwinedecor.in/product-category/customize-wallpaper/wall-mural-customize-wallpaper-7/

All products at ₹85/sqft.
None appear on the homepage (featured/best_seller/is_latest = False).

Run: python3 manage.py seed_leopard_tiger
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# (name, image_filename) — all at ₹85/sqft
LEOPARD_PRODUCTS = [
    ('Jaquar Noir Palace \u2013 Customize Wallpaper',
     'WhatsApp-Image-2026-02-15-at-11.59.46-AM.jpeg'),
    ('Tiger Bottlefreen ICustom Wallpaper',
     'Untitled-35.1.jpg'),
]

DESCRIPTION = (
    'Premium custom Leopard & Tiger wall mural, hand-crafted to transform '
    'your space with bold wildlife artistry. Made to order with high-quality '
    'materials for a luxurious finish. Priced per square foot.'
)


class Command(BaseCommand):
    help = 'Seed Leopard Tiger Wall Mural products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Leopard Tiger Wall Mural products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='wall-murals-leopard-tiger',
                defaults={
                    'name': 'Leopard Tiger',
                    'image': IMG_BASE + 'WhatsApp-Image-2026-02-15-at-11.59.46-AM.jpeg',
                    'sort_order': 13,
                    'is_active': True,
                }
            )
            if not created:
                cat.name = 'Leopard Tiger'
                cat.image = IMG_BASE + 'WhatsApp-Image-2026-02-15-at-11.59.46-AM.jpeg'
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
            for idx, (name, img_file) in enumerate(LEOPARD_PRODUCTS):
                img_url = IMG_BASE + img_file

                slug = slugify(name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=name,
                    slug=slug,
                    sku=f'LEO-{idx + 1:03d}',
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
            f'Seeded {product_count} Leopard Tiger Wall Mural products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
