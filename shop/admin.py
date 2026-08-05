from django.contrib import admin
from .models import (
    Category, Product, Room, Color, Testimonial,
    Review, Order, OrderItem, NewsletterSubscriber, ContactMessage,
    Country, Region, City, Notification,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'sort_order', 'is_active')
    list_filter = ('is_active', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'unit', 'featured', 'best_seller', 'is_latest', 'status')
    list_filter = ('category', 'status', 'featured', 'best_seller', 'is_latest')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'sku')
    list_editable = ('price', 'featured', 'best_seller', 'is_latest', 'status')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'location', 'rating', 'sort_order')
    list_editable = ('rating', 'sort_order')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rating', 'created_at')
    list_filter = ('rating',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('name', 'price', 'qty', 'unit')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'total', 'status', 'payment_status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('order_number', 'customer_name', 'email', 'phone', 'razorpay_order_id', 'razorpay_payment_id')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('order_number', 'total', 'created_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    inlines = [OrderItemInline]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)


# ---------------------------------------------------------------------------
# Geographic Catalog
# ---------------------------------------------------------------------------

class RegionInline(admin.TabularInline):
    model = Region
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


class CityInline(admin.TabularInline):
    model = City
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [RegionInline]


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'sort_order', 'is_active')
    list_filter = ('is_active', 'country')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [CityInline]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'featured', 'sort_order', 'is_active')
    list_filter = ('is_active', 'featured', 'region__country')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_editable = ('featured', 'sort_order', 'is_active')
