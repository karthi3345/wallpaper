from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.catalog, name='catalog'),
    path('category/<slug:slug>/', views.catalog, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    # Contact
    path('contact/', views.contact_us, name='contact_us'),
    # Auth
    path('login/', views.login_register, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    # Payment
    path('payment/<str:order_number>/', views.payment_page, name='payment_page'),
    path('payment/<str:order_number>/verify/', views.payment_verify, name='payment_verify'),
    path('payment/<str:order_number>/failed/', views.payment_failed, name='payment_failed'),
    # Newsletter
    path('newsletter/', views.newsletter_signup, name='newsletter'),
    # Geographic Catalog
    path('countries/', views.countries, name='countries'),
    path('countries/<slug:country_slug>/', views.country_detail, name='country_detail'),
    path('countries/<slug:country_slug>/<slug:region_slug>/', views.region_detail, name='region_detail'),
    path('countries/<slug:country_slug>/<slug:region_slug>/<slug:city_slug>/', views.city_detail, name='city_detail'),
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    # AI Wallpaper Generation
    path('ai-generate/', views.ai_generate, name='ai_generate'),
    path('ai-generate/create/', views.ai_generate_image, name='ai_generate_image'),
    # AI Decor Assistant Chatbot
    path('ai-chat/', views.ai_chat, name='ai_chat'),
]
