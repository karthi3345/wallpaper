from shop.models import Category, Notification


def cart_count(request):
    """Provide cart item count to all templates."""
    cart = request.session.get('cart', {})
    count = sum(cart.values()) if cart else 0
    return {'cart_count': count}


def categories(request):
    """Provide top-level categories to all templates."""
    return {
        'nav_categories': Category.objects.filter(
            parent__isnull=True, is_active=True
        ).order_by('sort_order', 'name')
    }


def notifications(request):
    """Provide unread notification count + recent notifications to all templates."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent = Notification.objects.filter(user=request.user).select_related('related_order')[:5]
        return {
            'unread_notifications': unread_count,
            'recent_notifications': recent,
        }
    return {
        'unread_notifications': 0,
        'recent_notifications': [],
    }
