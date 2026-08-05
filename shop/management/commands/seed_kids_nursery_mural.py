"""
Seed Kids & Nursery Wall Mural products matching the reference site exactly.
Products from: redandwinedecor.in/product-category/customize-wallpaper/wall/kids-nursary/

12 products, all at ₹85/sqft.
None appear on the homepage (featured/best_seller/is_latest = False).

Run: python3 manage.py seed_kids_nursery_mural
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import html
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# (name, image_filename) — all at ₹85/sqft
KIDS_NURSERY_PRODUCTS = [
    ('Palm Whisper – Luxury Neutral Botanical Mural Wallpaper',
     'Gemini_Generated_Image_dbqxkgdbqxkgdbqx.png'),
    ('Safari Serenity – Luxury Giraffe Mural Wallpaper',
     'Gemini_Generated_Image_71d7zu71d7zu71d7.png'),
    ('Dreamy Hot Air Balloon Adventure Kids I Wallpaper',
     'WhatsApp-Image-2025-09-16-at-5.10.00-PM-1.jpeg'),
    ('Forest Friends Adventure I Kidsroom Wallpaper',
     'WhatsApp-Image-2025-09-17-at-2.34.06-PM-1.jpeg'),
    ('Whimsical Mushroom House Kids I Wallpaper',
     'WhatsApp-Image-2025-09-15-at-3.20.21-PM-1.jpeg'),
    ('Rainbow Countryside Adventure I Kids Customize Wallpaper',
     'WhatsApp-Image-2025-09-12-at-6.49.29-PM-1.jpeg'),
    ('Fairy-Tale 3 Vintage Kids I Wallpaper',
     'WhatsApp-Image-2025-09-10-at-3.01.35-PM.jpeg'),
    ('Fairy-Tale 2 Vintage Kids I Wallpaper',
     'WhatsApp-Image-2025-09-10-at-3.01.34-PM.jpeg'),
    ('Fairy-Tale Vintage Kids I Wallpaper',
     'WhatsApp-Image-2025-09-10-at-3.01.34-PM-1.jpeg'),
    ('Mermaid Kids – Customize Wallpaper',
     '9.jpg'),
    ('Sky Night View Kids – Customize Wallcoverings',
     'DESIGNE-15.jpg'),
    ('Kids Balloon – Customize Wallcoverings',
     'DESIGNE-14.jpg'),
]

DESCRIPTION = (
    'Custom kids & nursery wall mural — hand-crafted to transform '
    'your child\'s room into a magical space. Made to order with '
    'high-quality materials for a luxurious finish. Priced per '
    'square foot.'
)


class Command(BaseCommand):
    help = 'Seed Kids & Nursery Wall Mural products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Kids & Nursery Wall Mural products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='wall-murals-kids-nursery',
                defaults={
                    'name': 'Kids & Nursery',
                    'image': IMG_BASE + 'Gemini_Generated_Image_dbqxkgdbqxkgdbqx.png',
                    'sort_order': 8,
                    'is_active': True,
                }
            )
            if not created:
                cat.name = 'Kids & Nursery'
                cat.image = IMG_BASE + 'Gemini_Generated_Image_dbqxkgdbqxkgdbqx.png'
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
            for idx, (name, img_file) in enumerate(KIDS_NURSERY_PRODUCTS):
                name = html.unescape(name)
                img_url = IMG_BASE + img_file

                slug = slugify(name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=name,
                    slug=slug,
                    sku=f'KN-{idx + 1:03d}',
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
            f'Seeded {product_count} Kids & Nursery Wall Mural products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
