from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max
from decimal import Decimal
import hmac
import hashlib
import json
import razorpay

from .models import (
    Category, Product, Room, Color, Testimonial,
    Review, Order, OrderItem, NewsletterSubscriber, ContactMessage,
    Country, Region, City, Notification,
)


def _get_cart(request):
    """Return cart dict from session: {product_id: qty}."""
    return request.session.get('cart', {})


def _get_cart_items(request):
    """Return list of (product, qty) from session cart with totals."""
    cart = _get_cart(request)
    items = []
    subtotal = Decimal('0')
    for pid_str, qty in cart.items():
        try:
            product = Product.objects.get(id=int(pid_str))
            line_total = product.price * qty
            subtotal += line_total
            items.append({
                'product': product,
                'qty': qty,
                'line_total': line_total,
            })
        except Product.DoesNotExist:
            continue
    return items, subtotal


def home(request):
    """Homepage with all sections."""
    # Featured product — exclude Glass Mosaic (homepage only)
    featured_product = Product.objects.filter(featured=True, status='active').exclude(category__slug='glass-mosaic-tiles').first()

    # Sale countdown — target end of day or a fixed future date
    sale_deadline = '2026-12-31T23:59:59'

    # Shop by category — top-level categories with images, exclude Glass Mosaic from home page
    categories = Category.objects.filter(parent__isnull=True, is_active=True).exclude(slug='glass-mosaic-tiles').order_by('sort_order', 'name')[:5]

    # Best sellers — exclude Glass Mosaic (homepage only)
    best_sellers = Product.objects.filter(best_seller=True, status='active').exclude(category__slug='glass-mosaic-tiles').order_by('-created_at')[:8]

    # Curated for modern spaces — exclude Glass Mosaic (homepage only)
    curated = Product.objects.filter(status='active').exclude(category__slug='glass-mosaic-tiles').exclude(id=featured_product.id if featured_product else None).order_by('-created_at')[:8]

    # Rooms
    rooms = Room.objects.all().order_by('sort_order')

    # Colors
    colors = Color.objects.all().order_by('sort_order')

    # Latest arrivals — exclude Glass Mosaic (homepage only)
    latest_arrivals = Product.objects.filter(is_latest=True, status='active').exclude(category__slug='glass-mosaic-tiles').order_by('-created_at')[:8]

    # Wallpaper of the week — exclude Glass Mosaic (homepage only)
    wallpaper_week = Product.objects.filter(featured=True, status='active').exclude(category__slug='glass-mosaic-tiles').first()
    if not wallpaper_week:
        wallpaper_week = Product.objects.filter(status='active').exclude(category__slug='glass-mosaic-tiles').first()

    # Featured collection — exclude Glass Mosaic (homepage only)
    featured_collection = Product.objects.filter(featured=True, status='active').exclude(category__slug='glass-mosaic-tiles').order_by('-created_at')[:10]
    if not featured_collection:
        featured_collection = Product.objects.filter(status='active').exclude(category__slug='glass-mosaic-tiles').order_by('-created_at')[:10]

    # Testimonials
    testimonials = Testimonial.objects.all().order_by('sort_order')

    # Countries for "Shop by Country" section
    countries = Country.objects.filter(is_active=True).order_by('sort_order', 'name')[:6]

    context = {
        'featured_product': featured_product,
        'sale_deadline': sale_deadline,
        'categories': categories,
        'best_sellers': best_sellers,
        'curated': curated,
        'rooms': rooms,
        'colors': colors,
        'latest_arrivals': latest_arrivals,
        'wallpaper_week': wallpaper_week,
        'featured_collection': featured_collection,
        'testimonials': testimonials,
        'countries': countries,
    }
    return render(request, 'home.html', context)


def catalog(request, slug=None):
    """Product listing with filtering."""
    products = Product.objects.filter(status='active')

    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        # Include products in this category and its subcategories
        subcats = category.children.all()
        if subcats.exists():
            products = products.filter(category__in=list(subcats) + [category])
        else:
            products = products.filter(category=category)

    # Filters
    selected_rooms = request.GET.getlist('room')
    selected_colors = request.GET.getlist('color')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort = request.GET.get('sort', 'newest')

    if selected_rooms:
        products = products.filter(rooms__slug__in=selected_rooms).distinct()
    if selected_colors:
        products = products.filter(colors__slug__in=selected_colors).distinct()
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Sorting
    sort_map = {
        'newest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # Price range for filter display
    price_range = Product.objects.filter(status='active').aggregate(
        min_price=Min('price'), max_price=Max('price')
    )

    all_rooms = Room.objects.all().order_by('sort_order')
    all_colors = Color.objects.all().order_by('sort_order')
    all_categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order')

    context = {
        'category': category,
        'products': products,
        'all_rooms': all_rooms,
        'all_colors': all_colors,
        'all_categories': all_categories,
        'selected_rooms': selected_rooms,
        'selected_colors': selected_colors,
        'price_min': price_min,
        'price_max': price_max,
        'price_range': price_range,
        'current_sort': sort,
    }
    return render(request, 'catalog.html', context)


def product_detail(request, slug):
    """Single product page."""
    product = get_object_or_404(Product, slug=slug, status='active')
    related = Product.objects.filter(category=product.category, status='active').exclude(id=product.id)[:4]
    reviews = product.reviews.all()[:6]

    context = {
        'product': product,
        'related_products': related,
        'reviews': reviews,
    }
    return render(request, 'product_detail.html', context)


@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    """Add product to session cart (login required)."""
    product = get_object_or_404(Product, id=product_id, status='active')
    cart = _get_cart(request)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items, subtotal = _get_cart_items(request)
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
            'subtotal': str(subtotal),
            'message': f'{product.name} added to cart',
        })

    messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def remove_from_cart(request, product_id):
    """Remove product from cart."""
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


def update_cart(request, product_id):
    """Update quantity in cart."""
    if request.method == 'POST':
        qty = int(request.POST.get('qty', 1))
        cart = _get_cart(request)
        pid = str(product_id)
        if qty > 0:
            cart[pid] = qty
        else:
            cart.pop(pid, None)
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Cart updated.')
    return redirect('cart')


def cart_view(request):
    """Shopping cart page."""
    items, subtotal = _get_cart_items(request)
    shipping = Decimal('0') if subtotal >= Decimal('5000') or subtotal == 0 else Decimal('250')
    total = subtotal + shipping
    context = {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'cart.html', context)


def checkout(request):
    """Checkout page — process order."""
    items, subtotal = _get_cart_items(request)
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('catalog')

    shipping = Decimal('0') if subtotal >= Decimal('5000') else Decimal('250')
    total = subtotal + shipping

    if request.method == 'POST':
        payment_method = request.POST.get('payment', 'cod')

        with transaction.atomic():
            order = Order.objects.create(
                order_number=Order.generate_order_number(),
                customer_name=request.POST.get('customer_name', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                pincode=request.POST.get('pincode', ''),
                total=total,
                status='pending',
                payment_status='unpaid' if payment_method == 'cod' else 'pending',
                payment_method=payment_method,
                user=request.user if request.user.is_authenticated else None,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    name=item['product'].name,
                    price=item['product'].price,
                    qty=item['qty'],
                    unit=item['product'].unit,
                )

        # Clear cart after order creation
        request.session['cart'] = {}
        request.session.modified = True

        if payment_method == 'online':
            return redirect('payment_page', order_number=order.order_number)

        return redirect('order_confirmation', order_number=order.order_number)

    context = {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'checkout.html', context)


def order_confirmation(request, order_number):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'order_confirmation.html', {'order': order})


# ---------------------------------------------------------------------------
# Razorpay payment views
# ---------------------------------------------------------------------------

def _get_razorpay_client():
    """Return a Razorpay client or None if credentials are missing (demo mode)."""
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    if not (key_id and key_secret):
        return None
    return razorpay.Client(auth=(key_id, key_secret))


def payment_page(request, order_number):
    """Render Razorpay Checkout (or demo-mode page) for an online order."""
    order = get_object_or_404(Order, order_number=order_number)

    # Guard: only online-payment orders that are pending or failed can access
    # the payment page. Failed orders are allowed so the user can retry.
    if order.payment_method != 'online' or order.payment_status not in ('pending', 'failed'):
        return redirect('order_confirmation', order_number=order.order_number)

    # Reset to pending if this is a retry after a previous failure
    if order.payment_status == 'failed':
        order.payment_status = 'pending'
        order.save(update_fields=['payment_status'])

    amount_paise = int(order.total * 100)  # Razorpay expects paise

    client = _get_razorpay_client()
    razorpay_order_id = None
    demo_mode = True

    if client:
        demo_mode = False
        # Create a Razorpay Order via the gateway API
        try:
            rzp_order = client.order.create({
                'amount': amount_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'receipt': order.order_number,
            })
            razorpay_order_id = rzp_order['id']
            order.razorpay_order_id = razorpay_order_id
            order.save(update_fields=['razorpay_order_id'])
        except Exception:
            # Gateway error — fall back to demo mode so the user isn't blocked
            demo_mode = True

    context = {
        'order': order,
        'amount_paise': amount_paise,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order_id,
        'demo_mode': demo_mode,
        'currency': settings.RAZORPAY_CURRENCY,
    }
    return render(request, 'payment.html', context)


@csrf_exempt
def payment_verify(request, order_number):
    """Verify the Razorpay payment signature after checkout."""
    if request.method != 'POST':
        return redirect('home')

    order = get_object_or_404(Order, order_number=order_number)

    # Already paid — redirect to confirmation
    if order.payment_status == 'paid':
        return redirect('order_confirmation', order_number=order.order_number)

    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    client = _get_razorpay_client()

    if client is None:
        # Demo mode — no Razorpay credentials configured.
        # Accept or reject based on the demo_result param.
        demo_result = request.POST.get('demo_result', 'success')
        if demo_result == 'success':
            order.razorpay_payment_id = f'demo_pay_{order.order_number}'
            order.razorpay_order_id = order.razorpay_order_id or f'demo_order_{order.order_number}'
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            return redirect('order_confirmation', order_number=order.order_number)
        else:
            order.payment_status = 'failed'
            order.razorpay_payment_id = f'demo_failed_{order.order_number}'
            order.save(update_fields=['payment_status', 'razorpay_payment_id'])
            return redirect('payment_failed', order_number=order.order_number)

    # Live mode — Razorpay credentials ARE configured.
    # A missing or invalid signature is ALWAYS a failure, never demo acceptance.
    if not razorpay_signature:
        order.payment_status = 'failed'
        order.razorpay_payment_id = razorpay_payment_id
        order.save(update_fields=['payment_status', 'razorpay_payment_id'])
        return redirect('payment_failed', order_number=order.order_number)

    # Verify HMAC-SHA256 signature
    key_secret = settings.RAZORPAY_KEY_SECRET
    msg = f'{razorpay_order_id}|{razorpay_payment_id}'
    expected = hmac.new(
        key_secret.encode('utf-8'),
        msg.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    if hmac.compare_digest(expected, razorpay_signature):
        # Verified — mark as paid
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_signature = razorpay_signature
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        return redirect('order_confirmation', order_number=order.order_number)
    else:
        order.payment_status = 'failed'
        order.razorpay_payment_id = razorpay_payment_id
        order.save(update_fields=['payment_status', 'razorpay_payment_id'])
        return redirect('payment_failed', order_number=order.order_number)


def payment_failed(request, order_number):
    """Payment failure page with retry option."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'payment_failed.html', {'order': order})


def newsletter_signup(request):
    """Newsletter signup handler."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thank you for subscribing!')
            else:
                messages.info(request, 'You are already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def contact_us(request):
    """Contact Us page with form and store info."""
    submitted = False
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            ContactMessage.objects.create(
                name=name, email=email, phone=phone, message=message,
            )
            submitted = True
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'contact_us.html', {'submitted': submitted})


def login_register(request):
    """Combined login / register page."""
    if request.user.is_authenticated:
        return redirect('home')

    login_error = None
    register_done = False

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')

        if form_type == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            remember = request.POST.get('remember')
            # Allow login by email OR username
            if '@' in username:
                try:
                    db_user = User.objects.get(email__iexact=username)
                    username = db_user.username
                except User.DoesNotExist:
                    pass
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if not remember:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('home')
            else:
                login_error = 'Invalid username or password.'

        elif form_type == 'register':
            email = request.POST.get('email', '').strip()
            if email:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'An account with this email already exists.')
                else:
                    username = email.split('@')[0]
                    base = username
                    i = 1
                    while User.objects.filter(username=username).exists():
                        username = f'{base}{i}'
                        i += 1
                    # Generate a random temporary password and email it
                    import secrets, string
                    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                    user = User.objects.create_user(username=username, email=email, password=temp_password)

                    # Send the password email
                    from django.core.mail import send_mail
                    try:
                        send_mail(
                            subject='Welcome to Mahashankh Decor — Your Account Details',
                            message=(
                                f'Welcome to Mahashankh Decor!\n\n'
                                f'Your account has been created successfully.\n\n'
                                f'Username: {username}\n'
                                f'Temporary Password: {temp_password}\n\n'
                                f'Please log in and change your password.\n\n'
                                f'Visit: https://mahashank.com/login/\n\n'
                                f'— Mahashankh Decor Team'
                            ),
                            from_email='noreply@mahashank.com',
                            recipient_list=[email],
                            fail_silently=True,
                        )
                    except Exception:
                        pass

                    register_done = True
                    messages.success(request, 'Registration successful! Your login details have been sent to your email.')
            else:
                messages.error(request, 'Please enter your email address.')

    return render(request, 'login_register.html', {
        'login_error': login_error,
        'register_done': register_done,
    })


def logout_view(request):
    """Log out and redirect home."""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ---------------------------------------------------------------------------
# Geographic Catalog — Shop by Country / Region / City
# ---------------------------------------------------------------------------

def countries(request):
    """List all active countries — alphabetical for the 195-country catalog."""
    countries = Country.objects.filter(is_active=True).order_by('name')
    total = countries.count()
    return render(request, 'countries.html', {
        'countries': countries,
        'total_countries': total,
    })


def country_detail(request, country_slug):
    """Show a country with its regions and featured wallpapers."""
    country = get_object_or_404(Country, slug=country_slug, is_active=True)
    regions = country.regions.filter(is_active=True).order_by('sort_order', 'name')

    # Featured wallpapers for this country: products linked to any city in this country
    products = Product.objects.filter(
        status='active', cities__region__country=country
    ).distinct().order_by('-created_at')[:12]

    # Featured cities (for a highlight grid)
    featured_cities = City.objects.filter(
        region__country=country, is_active=True, featured=True
    ).order_by('sort_order', 'name')[:8]

    # If no explicitly featured cities, show first few active ones
    if not featured_cities:
        featured_cities = City.objects.filter(
            region__country=country, is_active=True
        ).order_by('sort_order', 'name')[:8]

    context = {
        'country': country,
        'regions': regions,
        'products': products,
        'featured_cities': featured_cities,
    }
    return render(request, 'country_detail.html', context)


def region_detail(request, country_slug, region_slug):
    """Show a region with its cities and wallpapers."""
    country = get_object_or_404(Country, slug=country_slug, is_active=True)
    region = get_object_or_404(Region, slug=region_slug, country=country, is_active=True)
    cities = region.cities.filter(is_active=True).order_by('sort_order', 'name')

    # Wallpapers for this region
    products = Product.objects.filter(
        status='active', cities__region=region
    ).distinct().order_by('-created_at')[:12]

    context = {
        'country': country,
        'region': region,
        'cities': cities,
        'products': products,
    }
    return render(request, 'region_detail.html', context)


def city_detail(request, country_slug, region_slug, city_slug):
    """Show a city with its wallpapers in a grid."""
    country = get_object_or_404(Country, slug=country_slug, is_active=True)
    region = get_object_or_404(Region, slug=region_slug, country=country, is_active=True)
    city = get_object_or_404(City, slug=city_slug, region=region, is_active=True)

    # Wallpapers for this city
    products = Product.objects.filter(
        status='active', cities=city
    ).distinct().order_by('-created_at')

    # Other cities in the same region for navigation
    sibling_cities = City.objects.filter(
        region=region, is_active=True
    ).exclude(id=city.id).order_by('sort_order', 'name')[:6]

    context = {
        'country': country,
        'region': region,
        'city': city,
        'products': products,
        'sibling_cities': sibling_cities,
    }
    return render(request, 'city_detail.html', context)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

from django.contrib.auth.decorators import login_required


@login_required
def notification_list(request):
    """Full-page list of all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user).select_related('related_order')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read (redirects back)."""
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))


@login_required
def mark_all_notifications_read(request):
    """Mark all of the user's notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))


# ── AI Wallpaper Generation ──────────────────────────────────────────

@login_required(login_url='/login/')
def ai_generate(request):
    """AI image generation page — shows generator + public gallery (login required)."""
    from .ai_generator import AI_CATEGORIES
    from .models import AIGeneratedImage

    categories = [
        {'key': k, 'label': v['label'], 'icon': v['icon'],
         'description': v['description'], 'suggestions': v['suggestions']}
        for k, v in AI_CATEGORIES.items()
    ]
    recent_images = AIGeneratedImage.objects.filter(is_public=True)[:12]
    my_images = []
    if request.user.is_authenticated:
        my_images = AIGeneratedImage.objects.filter(user=request.user)[:8]

    context = {
        'ai_categories': categories,
        'recent_images': recent_images,
        'my_images': my_images,
    }
    return render(request, 'shop/ai_generate.html', context)


@require_http_methods(["POST"])
@login_required(login_url='/login/')
def ai_generate_image(request):
    """AJAX endpoint — generates an image and returns JSON (login required)."""
    from .ai_generator import AI_CATEGORIES, generate_image, classify_prompt
    from .models import AIGeneratedImage

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    prompt = (body.get('prompt') or '').strip()
    negative_prompt = (body.get('negative_prompt') or '').strip()
    category_key = (body.get('category') or '').strip()
    size = (body.get('size') or '1024x1024').strip()

    if not prompt:
        return JsonResponse({'error': 'Please describe what you want to generate.'}, status=400)
    if not prompt or len(prompt) < 3:
        return JsonResponse({'error': 'Please enter a longer description (at least 3 characters).'}, status=400)
    if category_key not in AI_CATEGORIES:
        return JsonResponse({'error': 'Please select a valid category.'}, status=400)

    valid_sizes = ('1024x1024', '1792x1024', '1024x1792')
    if size not in valid_sizes:
        size = '1024x1024'

    b64_data, error = generate_image(prompt, category_key, size, negative_prompt)
    if error:
        return JsonResponse({'error': error}, status=500)

    # Save image to filesystem
    import base64, uuid
    from django.core.files.base import ContentFile
    filename = f'ai_{uuid.uuid4().hex[:12]}.png'
    image_file = ContentFile(base64.b64decode(b64_data))
    cat_label = AI_CATEGORIES[category_key]['label']
    enhanced = classify_prompt(prompt, category_key)

    ai_img = AIGeneratedImage(
        category_key=category_key,
        prompt=prompt,
        negative_prompt=negative_prompt,
        enhanced_prompt=enhanced,
        size=size,
        user=request.user if request.user.is_authenticated else None,
    )
    ai_img.image.save(filename, image_file, save=False)
    ai_img.save()

    return JsonResponse({
        'success': True,
        'image_url': ai_img.image.url,
        'category_label': cat_label,
        'category_icon': AI_CATEGORIES[category_key]['icon'],
        'prompt': prompt,
        'created_id': ai_img.id,
    })


# ── AI Decor Assistant Chatbot ───────────────────────────────────────

@require_http_methods(["POST"])
@login_required(login_url='/login/')
def ai_chat(request):
    """
    AJAX endpoint for the Mistral-powered decor assistant chatbot (login required).

    Accepts JSON: { "message": "...", "history": [{"from": "bot"|"user", "text": "..."}] }
    Returns JSON: { "reply": "...", "source": "ai"|"fallback" }
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = (body.get('message') or '').strip()
    history = body.get('history') or []

    if not message:
        return JsonResponse({'error': 'Message is required.'}, status=400)

    # Cap history at 20 entries to prevent abuse
    if isinstance(history, list) and len(history) > 20:
        history = history[-20:]

    from .decor_assistant import get_ai_response, get_keyword_fallback

    reply, error = get_ai_response(message, history)

    if reply:
        return JsonResponse({'reply': reply, 'source': 'ai'})

    # Fallback to keyword-based reply
    fallback = get_keyword_fallback(message)
    return JsonResponse({
        'reply': fallback,
        'source': 'fallback',
        'note': 'AI service temporarily unavailable — showing a quick answer.',
    })
