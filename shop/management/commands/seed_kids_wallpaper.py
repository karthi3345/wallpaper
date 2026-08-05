"""
Seed Kids Wallpaper products matching the reference site exactly.
Products from: redandwinedecor.in/product-category/wallpaper-roll/kids-wallpaper/

17 products: 9 "Buy 01 Get 01" at ₹599 (regular ₹3,599) + 8 "Kid's PVC" at ₹294 (regular ₹1,499–₹1,999).
None appear on the homepage (featured/best_seller/is_latest = False).

Run: python3 manage.py seed_kids_wallpaper
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import html
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# (name, sku, image_filename, price, compare_at_price)
KIDS_PRODUCTS = [
    # --- "Buy 01 Get 01" series — ₹599, was ₹3,599 ---
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160204D", 'ZT160204D',
     'A2DF1833-E5C8-4C8B-AD56-71E4125C369E.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160207A", 'ZT160207A',
     'FD140682-48A5-43FD-9510-10F380C83C7C.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160208C", 'ZT160208C',
     'A67A5D6A-B5F0-493A-A8C9-0EFEB5A802A4.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160210B", 'ZT160210B',
     '531F4EC5-AE8F-4B87-97B9-378CEBF60A15.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160212C", 'ZT160212C',
     '531F4EC5-AE8F-4B87-97B9-378CEBF60A15.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160214C", 'ZT160214C',
     'BCE78B39-2504-4DA8-A336-5AE7E656FC18.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160214D", 'ZT160214D',
     'BA64911E-B4EF-4C08-91ED-1BE0A57BAE1A.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160218D", 'ZT160218D',
     '6F3A6284-0D76-4866-970B-4BC0D99899D3.png', Decimal('599'), Decimal('3599')),
    ("Buy 01 Get 01 Kid's – PVC Wallpaper ZT160219A", 'ZT160219A',
     '20-scaled-1.jpg', Decimal('599'), Decimal('3599')),

    # --- "Kid's PVC Wallpaper" series — ₹294, was ₹1,499–₹1,999 ---
    ("Kid's – PVC Wallpaper ZT160207B", 'ZT160207B',
     '11-scaled-1.jpg', Decimal('294'), Decimal('1499')),
    ("Kid's – PVC Wallpaper ZT160207D", 'ZT160207D',
     '9-scaled-1.jpg', Decimal('294'), Decimal('1999')),
    ("Kid's – PVC Wallpaper ZT160208D", 'ZT160208D',
     '13-scaled-1.jpg', Decimal('294'), Decimal('1499')),
    ("Kid's – PVC Wallpaper ZT160216B", 'ZT160216B',
     'WhatsApp-Image-2026-07-13-at-9.45.24-PM-1.jpeg', Decimal('294'), Decimal('1499')),
    ("Kid's – PVC Wallpaper ZT160216C", 'ZT160216C',
     'WhatsApp-Image-2026-07-13-at-9.45.24-PM-2.jpeg', Decimal('294'), Decimal('1499')),
    ("Kid's – PVC Wallpaper ZT160218B", 'ZT160218B',
     '10-scaled-1.jpg', Decimal('294'), Decimal('1499')),
    ("Kid's – PVC Wallpaper ZT160218E", 'ZT160218E',
     '64099817-5AC6-4A82-8BFA-AAAACB1333A6.png', Decimal('294'), Decimal('1499')),
    ("Kid's Manchester United – PVC Wallpaper 88807-1", '88807-1',
     'WhatsApp-Image-2026-07-13-at-9.45.27-PM.jpeg', Decimal('294'), Decimal('1599')),
]

DESCRIPTION = (
    'Kid\'s PVC wallpaper — durable, washable, and easy to install. '
    'Perfect for children\'s bedrooms, playrooms, and nurseries. '
    'Made from high-quality PVC material that is waterproof and '
    'long-lasting. Bright, fun designs that kids will love.'
)


class Command(BaseCommand):
    help = 'Seed Kids Wallpaper products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Kids Wallpaper products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='wallpaper-rolls-kids',
                defaults={
                    'name': 'Kids',
                    'image': IMG_BASE + 'FD140682-48A5-43FD-9510-10F380C83C7C.png',
                    'sort_order': 8,
                    'is_active': True,
                }
            )
            if not created:
                cat.name = 'Kids'
                cat.image = IMG_BASE + 'FD140682-48A5-43FD-9510-10F380C83C7C.png'
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
            for idx, (name, sku, img_file, price, compare_at) in enumerate(KIDS_PRODUCTS):
                name = html.unescape(name)
                img_url = IMG_BASE + img_file

                slug = slugify(name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=name,
                    slug=slug,
                    sku=sku,
                    description=DESCRIPTION,
                    short_description=name,
                    price=price,
                    compare_at_price=compare_at,
                    unit='pc',
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
            f'Seeded {product_count} Kids Wallpaper products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
