"""
Seed PAINTINGS/ WALLART products matching the reference site exactly.
Products, names, prices, and image URLs from:
redandwinedecor.in/product-category/paintings-wallart/

All 46 products across 3 pages, all priced per piece (pc).
None appear on the homepage (featured/best_seller/is_latest = False).

Run: python3 manage.py seed_paintings
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color
from decimal import Decimal
import random

IMG_BASE = 'https://redandwinedecor.in/wp-content/uploads/2026/03/'

# Exact products from WooCommerce Store API (category 182)
# (name, price, image_filename)
PAINTINGS_PRODUCTS = [
    # Page 1 (16 products)
    ('A captivating fine art photograph', '5200', 'Image-22.jpeg'),
    ('Abstract Ballerina Dancers', '2400', '3.jpeg'),
    ('Abstract Sailboat Wall Art', '3500', 'image-23-1.jpeg'),
    ('Abstract Teal and Gold Horizon\u201d Hand-Painted Wall Art', '3900', 'Image-2.jpeg'),
    ('Abstract Textured Wall Art', '3500', 'Image-34-1.jpeg'),
    ('Abstract, Textured wall art', '2100', '2.jpeg'),
    ('African Savanna Landscape', '1800', 'Image-33.jpeg'),
    ('African woman \u2013 Beauty, Strength and Cultural richness.', '2100',
     'WhatsApp-Image-2026-01-10-at-12.58.06-PM.jpeg'),
    ('Azure Ginkgo Garden', '2100', 'Image-3.jpeg'),
    ('Blend of Tropical scenery', '1800',
     'WhatsApp-Image-2026-01-10-at-12.58.05-PM-1.jpeg'),
    ('Blooming Lotus Flowers', '5599', 'Image-34.jpeg'),
    ('Buddha an aura of peace, wisdom, and tranquility', '5799', 'Image-15.jpeg'),
    ('Calming Beauty of Nature Wall Art', '5600', '4.jpeg'),
    ('Contemporary Art \u2013 Traditional African theme', '1800', '1.jpeg'),
    ('Crimson Elegance: A Modern Fashion Wall Art', '3500', 'Image-18.jpeg'),
    ('Desert landscape with flowing sand dunes', '10200', 'image-9.jpeg'),

    # Page 2 (16 products)
    ('Dynamic \u201cSpanish Dance\u201d Abstract Wall Art', '2100',
     'WhatsApp-Image-2026-01-10-at-12.58.05-PM.jpeg'),
    ('Elegant 3D White Flower Textured Wall Art', '3100', 'image-26.jpeg'),
    ('Elegant Blue & White Floral Butterfly Wall Art', '3500', 'image-24.jpeg'),
    ('Elegant wall art \u2013 Golden lotus flowers', '4600', 'image-13.jpeg'),
    ('Ethereal art print \u2013 Graceful woman', '3500', 'Image-21.jpeg'),
    ('Ethereal Bloom\u201d Textured White Flower Wall Art', '5900', 'image-27.jpeg'),
    ('Ethereal Majesty\u201d \u2013 Swan in Flight Canvas Wall Art', '4600', 'Image-20.jpeg'),
    ('Ethereal Reverie\u201d Canvas Art Print', '2200', 'Image-7.jpeg'),
    ('Expressive abstract painting', '3500', 'Image-19.jpeg'),
    ('Exquisite Ginkgo Leaf Wall Art', '3500', 'image-18a.jpeg'),
    ('Golden Grove Reflections \u2013 3D Classic Nature Art', '1800', 'image-4.jpeg'),
    ('Golden Grove Reflections \u2013 3D Classic Nature Art (Copy)', '1800', 'image-4.jpeg'),
    ('Imported Black abstract Emboss sparks I Canvas Painting', '5899',
     'WhatsApp-Image-2025-11-26-at-07.21.09_506bacc8.jpg'),
    ('Imported Buddha Face Painting', '5899',
     'WhatsApp-Image-2025-11-26-at-07.21.12_f6568340.jpg'),
    ('Imported Crystal Wall ART', '6650',
     'ChatGPT-Image-Dec-7-2025-05_23_35-PM.png'),
    ('Imported Golden Abstract Shell Texture I Wall Painting', '5899',
     'WhatsApp-Image-2025-11-26-at-07.21.10_862ca918.jpg'),

    # Page 3 (14 products)
    ('Imported Horse Light weight I Canvas Painting', '5899',
     'WhatsApp-Image-2025-11-26-at-07.21.10_a30204fd.jpg'),
    ('Imported Modern Landscape \u2013 Wall Painting', '15399',
     'WhatsApp-Image-2025-11-26-at-07.21.11_dfa77299.jpg'),
    ('Lady on Balcony: Captivating Wall Art', '2100', 'image-8.jpeg'),
    ('Majestic Feather Abstract Textured Wall Art', '3100', 'Image-14.jpeg'),
    ('Minimalist Geometric 3D Relief Wall Art', '3100', 'Image-35.jpeg'),
    ('Modern Abstract Floral Canvas Wall Art', '10200', 'Image-16.jpeg'),
    ('Modern Abstract LED Line Art', '5200', 'image-12.jpeg'),
    ('Neon abstract guitar wall art', '4600', 'image-10.jpeg'),
    ('Premium Imported \u201cGolden Sun Elephant\u201d Wall Painting', '15399',
     'WhatsApp-Image-2025-11-26-at-07.21.10_c68beef3.jpg'),
    ('Premium Imported \u201cHeritage Clock Tower\u201d Wall Painting', '15399',
     'WhatsApp-Image-2025-11-26-at-07.21.11_14682c40.jpg'),
    ('Red Flamingo with a distinct glittering', '4600', 'image-17.jpeg'),
    ('Retro women wall art', '2100', 'image-28.jpeg'),
    ('Surrealist Wall Art', '4800', 'Image-23.jpeg'),
    ('Zen Garden Harmony', '2500', 'image-5.jpeg'),
]

DESCRIPTION = (
    'Premium quality wall art and painting, perfect for adding a touch of '
    'elegance to any room. Each piece is carefully crafted to bring beauty '
    'and character to your living space. Suitable for living rooms, bedrooms, '
    'offices, and gifting.'
)


class Command(BaseCommand):
    help = 'Seed PAINTINGS/ WALLART products matching reference site'

    def handle(self, *args, **options):
        self.stdout.write('Seeding PAINTINGS/ WALLART products...')

        with transaction.atomic():
            cat, created = Category.objects.get_or_create(
                slug='paintings-wallart',
                defaults={
                    'name': 'PAINTINGS/ WALLART',
                    'image': IMG_BASE + 'Image-22.jpeg',
                    'sort_order': 10,
                    'is_active': True,
                }
            )
            if not created:
                cat.name = 'PAINTINGS/ WALLART'
                cat.image = IMG_BASE + 'Image-22.jpeg'
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
            for idx, (name, price, img_file) in enumerate(PAINTINGS_PRODUCTS):
                img_url = IMG_BASE + img_file

                # Generate unique slug
                slug = slugify(name)
                if Product.objects.filter(slug=slug).exists():
                    slug = f'{slug}-{idx}'

                product = Product.objects.create(
                    category=cat,
                    name=name,
                    slug=slug,
                    sku=f'PAINT-{idx + 1:03d}',
                    description=DESCRIPTION,
                    short_description=name,
                    price=Decimal(price),
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
            f'Seeded {product_count} PAINTINGS/ WALLART products. '
            f'Total in category: {Product.objects.filter(category=cat).count()}'
        ))
