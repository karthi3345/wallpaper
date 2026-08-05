"""
Seed demo data for Mahashank.
Run: python3 manage.py seed_demo
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Product, Room, Color, Testimonial, Review
from decimal import Decimal
import random

# Image pools — Unsplash for wallpaper/decor demo imagery
WALLPAPER_IMAGES = [
    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800',
    'https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=800',
    'https://images.unsplash.com/photo-1558211583-d26f610c1eb1?w=800',
    'https://images.unsplash.com/photo-1567016432779-094069958ea5?w=800',
    'https://images.unsplash.com/photo-1615529182904-14819c35db37?w=800',
    'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800',
    'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=800',
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800',
    'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800',
    'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800',
    'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=800',
    'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800',
    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800',
    'https://images.unsplash.com/photo-1567016432779-094069958ea5?w=800',
]

DECOR_IMAGES = [
    'https://images.unsplash.com/photo-1513519245088-0e12902e3564?w=800',
    'https://images.unsplash.com/photo-1517991104123-1d56a6e81ed9?w=800',
    'https://images.unsplash.com/photo-1499933374294-4584851497cc?w=800',
    'https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800',
    'https://images.unsplash.com/photo-1531873984280-04ee20ee9d8d?w=800',
]

ROOM_IMAGES = {
    'Living Room': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200',
    'Bedroom': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200',
    'Dining Room': 'https://images.unsplash.com/photo-1617806118233-18e1de247200?w=1200',
    'Hallway': 'https://images.unsplash.com/photo-1594026984060-3e5b9b3b1a3e?w=1200',
    'Study Room': 'https://photos.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200',
    'Kids Room': 'https://images.unsplash.com/photo-1558211583-d26f610c1eb1?w=1200',
    'Bathroom': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=1200',
}

CATEGORY_DATA = {
    'Wall Murals': {
        'image': WALLPAPER_IMAGES[0],
        'children': ['Heritage', 'European', 'Pichwai', 'Temple', 'Tropical',
                      'Chinoiseries', 'Leopard Tiger', 'Ceiling', 'Kids & Nursery',
                      'Seamless', '3D Wallmural', 'Peacock'],
    },
    'Wallpaper Rolls': {
        'image': WALLPAPER_IMAGES[1],
        'children': ['Luxury Series', 'Damask', 'Office', 'Floral', 'Abstract',
                      'Kids', 'Metallic', 'Texture'],
    },
    'Paintings & Wallart': {
        'image': DECOR_IMAGES[0],
        'children': [],
    },
    'Glass Mosaic Tiles': {
        'image': DECOR_IMAGES[1],
        'children': [],
    },
    'Home Decor': {
        'image': DECOR_IMAGES[2],
        'children': [],
    },
    'Self Adhesive Wallpaper': {
        'image': WALLPAPER_IMAGES[2],
        'children': [],
    },
}

ROOM_DATA = ['Living Room', 'Bedroom', 'Dining Room', 'Hallway', 'Study Room', 'Kids Room', 'Bathroom']

COLOR_DATA = [
    ('Warm Neutrals', '#D4B996'),
    ('Earthy Browns', '#8B5E3C'),
    ('Cool Grays', '#9CA3AF'),
    ('Soft Blues', '#7BA7BC'),
    ('Sage & Greens', '#9CAF88'),
]

TESTIMONIAL_DATA = [
    ('Priya Sharma', 'Mumbai, Maharashtra', 'Absolutely stunning wallpapers! The quality exceeded my expectations. My living room looks like a magazine cover now.', 5),
    ('Rajesh Kumar', 'Delhi, Delhi', 'The heritage mural we ordered is breathtaking. Installation was smooth and the team was very professional.', 5),
    ('Ananya Patel', 'Bangalore, Karnataka', 'Beautiful designs and excellent customer service. Highly recommend Mahashank for anyone looking to transform their space.', 5),
    ('Vikram Singh', 'Jaipur, Rajasthan', 'The Pichwai mural in our dining room is a conversation starter at every dinner party. Love it!', 5),
    ('Meera Iyer', 'Chennai, Tamil Nadu', 'Premium quality wallpapers at reasonable prices. The peacock mural is simply gorgeous.', 4),
    ('Arjun Reddy', 'Hyderabad, Telangana', 'Fast delivery and the wallpaper was exactly as shown. Will definitely order again.', 5),
    ('Sneha Gupta', 'Pune, Maharashtra', 'The color palette options helped me choose the perfect wallpaper for my bedroom. Very happy!', 5),
    ('Karthik Nair', 'Kochi, Kerala', 'Outstanding craftsmanship. The European mural added so much character to our home.', 5),
]

PRODUCT_NAME_TEMPLATES = {
    'Wall Murals': [
        '{sub} Mural — {variant}', '{sub} Wall Art — {variant}', '{sub} Designer Mural — {variant}',
    ],
    'Wallpaper Rolls': [
        '{sub} Wallpaper Roll — {variant}', '{sub} Designer Roll — {variant}',
    ],
    'default': ['{cat} — {variant}', '{cat} Collection — {variant}'],
}

VARIANTS = ['Gold Leaf', 'Royal Blue', 'Emerald Green', 'Burgundy Wine', 'Ivory Cream',
            'Charcoal Black', 'Pearl White', 'Antique Bronze', 'Rose Quartz', 'Sapphire Mist',
            'Terracotta', 'Slate Gray', 'Mauve Blush', 'Forest Deep', 'Champagne Gold',
            'Ocean Teal', 'Desert Sand', 'Midnight Velvet']

PRODUCT_DESCRIPTIONS = [
    'Transform your walls with this exquisite designer wallpaper, crafted to bring elegance and sophistication to any room. Made from premium materials with a smooth matte finish, this wallpaper is both durable and easy to maintain. Perfect for creating a statement wall in your living room, bedroom, or office space.',
    'Elevate your interior with this stunning piece from our curated collection. Each design is meticulously crafted to reflect timeless beauty and modern aesthetics. The high-quality material ensures longevity while the intricate patterns add depth and character to your walls.',
    'A masterpiece for your walls — this premium wallpaper combines traditional artistry with contemporary design. The rich textures and detailed patterns create a luxurious ambiance that transforms any space into a work of art.',
]


class Command(BaseCommand):
    help = 'Seed demo data for Mahashank'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        with transaction.atomic():
            # Clear existing
            Product.objects.all().delete()
            Category.objects.all().delete()
            Room.objects.all().delete()
            Color.objects.all().delete()
            Testimonial.objects.all().delete()
            Review.objects.all().delete()

            # Create categories
            categories = {}
            subcategories = {}
            for order, (cat_name, data) in enumerate(CATEGORY_DATA.items()):
                cat = Category.objects.create(
                    name=cat_name,
                    slug=slugify(cat_name),
                    image=data['image'],
                    sort_order=order,
                )
                categories[cat_name] = cat
                for sub_order, sub_name in enumerate(data['children']):
                    sub = Category.objects.create(
                        name=sub_name,
                        slug=slugify(f"{cat_name}-{sub_name}"),
                        parent=cat,
                        image=random.choice(WALLPAPER_IMAGES),
                        sort_order=sub_order,
                    )
                    subcategories[sub_name] = sub

            # Create rooms
            rooms = {}
            for order, room_name in enumerate(ROOM_DATA):
                room = Room.objects.create(
                    name=room_name,
                    slug=slugify(room_name),
                    image=ROOM_IMAGES.get(room_name, ROOM_IMAGES['Living Room']),
                    sort_order=order,
                )
                rooms[room_name] = room

            # Create colors
            colors = {}
            for order, (color_name, hex_code) in enumerate(COLOR_DATA):
                color = Color.objects.create(
                    name=color_name,
                    slug=slugify(color_name),
                    hex_code=hex_code,
                    image=random.choice(WALLPAPER_IMAGES),
                    sort_order=order,
                )
                colors[color_name] = color

            # Create products
            product_count = 0
            for cat_name, data in CATEGORY_DATA.items():
                cat = categories[cat_name]
                if data['children']:
                    # Products in subcategories
                    for sub_name in data['children']:
                        sub = subcategories[sub_name]
                        templates = PRODUCT_NAME_TEMPLATES.get(cat_name, PRODUCT_NAME_TEMPLATES['default'])
                        for i in range(3):  # 3 products per subcategory
                            variant = random.choice(VARIANTS)
                            name = random.choice(templates).format(sub=sub_name, variant=variant, cat=cat_name)
                            slug_base = slugify(name)
                            price = Decimal(random.choice([85, 120, 150, 200, 250, 300, 350, 450, 500, 600, 750, 900, 1000, 1200, 1500, 2000, 3000]))

                            unit = 'sqft' if 'Mural' in cat_name or 'Adhesive' in cat_name else 'pc'
                            img = random.choice(WALLPAPER_IMAGES)
                            product = Product.objects.create(
                                category=sub,
                                name=name,
                                slug=f'{slug_base}-{product_count + 1}',
                                sku=f'RWD-{cat_name[:3].upper()}-{product_count + 1:04d}',
                                description=random.choice(PRODUCT_DESCRIPTIONS),
                                short_description=f'Premium {sub_name} wallpaper',
                                price=price,
                                compare_at_price=price + Decimal(random.choice([100, 200, 300, 500])) if random.random() > 0.5 else None,
                                unit=unit,
                                images=[img, random.choice(WALLPAPER_IMAGES), random.choice(WALLPAPER_IMAGES)],
                                featured=product_count < 5,
                                best_seller=random.random() > 0.6,
                                is_latest=product_count % 3 == 0,
                                status='active',
                                sort_order=product_count,
                            )
                            # Assign random rooms and colors
                            product.rooms.set(random.sample(list(rooms.values()), random.randint(1, 3)))
                            product.colors.set(random.sample(list(colors.values()), random.randint(1, 2)))
                            product_count += 1
                else:
                    # Products directly in top-level category
                    templates = PRODUCT_NAME_TEMPLATES.get(cat_name, PRODUCT_NAME_TEMPLATES['default'])
                    for i in range(5):
                        variant = random.choice(VARIANTS)
                        name = random.choice(templates).format(cat=cat_name, variant=variant, sub=cat_name)
                        slug_base = slugify(name)
                        price = Decimal(random.choice([200, 300, 400, 500, 600, 750, 900, 1200, 1500, 2000]))
                        img = random.choice(WALLPAPER_IMAGES + DECOR_IMAGES)
                        unit = 'sqft' if 'Adhesive' in cat_name else 'pc'
                        product = Product.objects.create(
                            category=cat,
                            name=name,
                            slug=f'{slug_base}-{product_count + 1}',
                            sku=f'RWD-{cat_name[:3].upper()}-{product_count + 1:04d}',
                            description=random.choice(PRODUCT_DESCRIPTIONS),
                            short_description=f'Premium {cat_name}',
                            price=price,
                            compare_at_price=price + Decimal(random.choice([100, 200, 300])) if random.random() > 0.5 else None,
                            unit=unit,
                            images=[img, random.choice(WALLPAPER_IMAGES), random.choice(WALLPAPER_IMAGES)],
                            featured=product_count < 5,
                            best_seller=random.random() > 0.6,
                            is_latest=product_count % 3 == 0,
                            status='active',
                            sort_order=product_count,
                        )
                        product.rooms.set(random.sample(list(rooms.values()), random.randint(1, 3)))
                        product.colors.set(random.sample(list(colors.values()), random.randint(1, 2)))
                        product_count += 1

            # Create testimonials
            for order, (author, location, content, rating) in enumerate(TESTIMONIAL_DATA):
                Testimonial.objects.create(
                    author=author,
                    location=location,
                    content=content,
                    rating=rating,
                    image=f'https://images.unsplash.com/photo-{random.choice(["1494790108377-be9c29b29330", "1507003211169-0a1dd7228f2d", "1499952127939-9bbf5af6c51c", "1438761681033-6461ffad8d80"])}?w=200',
                    sort_order=order,
                )

            # Create reviews for first few products
            first_products = Product.objects.all()[:10]
            review_authors = ['Aarav', 'Diya', 'Ishaan', 'Ananya', 'Vihaan', 'Saanvi', 'Aditya', 'Kiara']
            for product in first_products:
                for j in range(random.randint(2, 4)):
                    Review.objects.create(
                        product=product,
                        author=random.choice(review_authors),
                        rating=random.choice([4, 5, 5, 5]),
                        content=random.choice([
                            'Absolutely love this! The quality is amazing.',
                            'Beautiful design, looks even better in person.',
                            'Exceeded my expectations. Highly recommend!',
                            'Perfect addition to my home decor.',
                            'Great value for the price. Very satisfied.',
                        ]),
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded: {Category.objects.count()} categories, {Product.objects.count()} products, '
            f'{Room.objects.count()} rooms, {Color.objects.count()} colors, '
            f'{Testimonial.objects.count()} testimonials, {Review.objects.count()} reviews'
        ))
