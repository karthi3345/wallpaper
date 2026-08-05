from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.URLField(blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    image = models.URLField(blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    hex_code = models.CharField(max_length=7, default='#cccccc')
    image = models.URLField(blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    short_description = models.CharField(max_length=300, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, default='pc')  # 'pc' or 'sqft'
    images = models.JSONField(default=list, blank=True)
    rooms = models.ManyToManyField(Room, blank=True)
    colors = models.ManyToManyField(Color, blank=True)
    cities = models.ManyToManyField('City', blank=True, related_name='city_products')
    featured = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def main_image(self):
        if self.images and len(self.images) > 0:
            return self.images[0]
        return 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600'


class Testimonial(models.Model):
    author = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, default='')
    content = models.TextField()
    rating = models.IntegerField(default=5)
    image = models.URLField(blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.author} ({self.rating}★)'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=100)
    rating = models.IntegerField(default=5)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} — {self.product.name} ({self.rating}★)'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    razorpay_order_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_signature = models.CharField(max_length=200, blank=True, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} — {self.customer_name}'

    @staticmethod
    def generate_order_number():
        import uuid
        return 'RWD-' + uuid.uuid4().hex[:8].upper()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, default='pc')

    def __str__(self):
        return f'{self.name} x{self.qty}'

    @property
    def line_total(self):
        return self.price * self.qty


class Country(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    image = models.URLField(blank=True, default='', max_length=1000)
    description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('country_detail', kwargs={'country_slug': self.slug})

    @property
    def product_count(self):
        """Count all products associated with any city in this country."""
        return Product.objects.filter(cities__region__country=self).distinct().count()


class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    image = models.URLField(blank=True, default='', max_length=1000)
    description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.name}, {self.country.name}'

    def get_absolute_url(self):
        return reverse('region_detail', kwargs={
            'country_slug': self.country.slug, 'region_slug': self.slug
        })

    @property
    def product_count(self):
        return Product.objects.filter(cities__region=self).distinct().count()


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    image = models.URLField(blank=True, default='', max_length=1000)
    description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.name}, {self.region.name}'

    def get_absolute_url(self):
        return reverse('city_detail', kwargs={
            'country_slug': self.region.country.slug,
            'region_slug': self.region.slug,
            'city_slug': self.slug,
        })

    @property
    def product_count(self):
        return self.city_products.filter(status='active').count()


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default='')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.email}'


class Notification(models.Model):
    """Persistent in-app notification — login/logout tracking, delivery updates, etc."""
    TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('order_delivered', 'Order Delivered'),
        ('order_placed', 'Order Placed'),
        ('order_shipped', 'Order Shipped'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.title}'

    @property
    def icon(self):
        """Return an emoji icon based on notification type."""
        icons = {
            'login': '🔑',
            'logout': '🚪',
            'order_delivered': '📦',
            'order_placed': '🛒',
            'order_shipped': '🚚',
        }
        return icons.get(self.notification_type, '🔔')


class AIGeneratedImage(models.Model):
    """Stores AI-generated wallpaper/mural/painting images."""
    CATEGORY_CHOICES = [
        ('painting', 'AI Painting'),
        ('mural', 'AI Wall Mural'),
        ('wallpaper', 'AI Wallpaper Roll'),
        ('wall-art', 'AI Wall Art'),
        ('texture', 'AI Texture'),
        ('kids-nursery', 'AI Kids & Nursery'),
        ('3d-mural', 'AI 3D Mural'),
        ('ceiling', 'AI Ceiling Art'),
    ]
    SIZE_CHOICES = [
        ('1024x1024', 'Square (1024×1024)'),
        ('1792x1024', 'Landscape (1792×1024)'),
        ('1024x1792', 'Portrait (1024×1792)'),
    ]

    category_key = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, default='')
    enhanced_prompt = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='ai_generated/')
    size = models.CharField(max_length=20, default='1024x1024')
    is_public = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_images')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_category_key_display()} — {self.prompt[:50]}'

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category_key, self.category_key)

    @property
    def category_icon(self):
        icons = {
            'painting': '🎨', 'mural': '🏛️', 'wallpaper': '🪞', 'wall-art': '🖼️',
            'texture': '✨', 'kids-nursery': '🧸', '3d-mural': '🌀', 'ceiling': '🌌',
        }
        return icons.get(self.category_key, '🎨')
