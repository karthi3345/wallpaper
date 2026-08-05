"""Signal handlers for the notification system.

Creates notifications on:
- user_logged_in  → login notification
- user_logged_out → logout notification
- Order status change to 'delivered' → delivery notification (with product names)
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Notification, Order


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """Capture the old status before save so post_save can detect transitions."""
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(user_logged_in)
def create_login_notification(sender, request, user, **kwargs):
    """Fire a notification when a user logs in."""
    Notification.objects.create(
        user=user,
        notification_type='login',
        title='Login Successful',
        message=f'You logged in to your account on {timezone.now().strftime("%d %b %Y at %I:%M %p")}.',
    )


@receiver(user_logged_out)
def create_logout_notification(sender, request, user, **kwargs):
    """Fire a notification when a user logs out."""
    if user is None:
        return
    Notification.objects.create(
        user=user,
        notification_type='logout',
        title='Logout Recorded',
        message=f'You logged out of your account on {timezone.now().strftime("%d %b %Y at %I:%M %p")}.',
    )


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    """When an order's status changes to 'delivered', notify the linked user
    (or any user matching the order's email) with a product breakdown.

    Uses a private attribute set by the pre_save signal above to detect
    the transition. Note: queryset .update() bypasses signals, so only
    .save() triggers this handler.
    """
    old_status = getattr(instance, '_old_status', None)

    if instance.status == 'delivered' and old_status != 'delivered':
        # Determine which user(s) to notify
        recipients = []
        if instance.user:
            recipients.append(instance.user)
        else:
            # Fallback: match by email
            from django.contrib.auth.models import User
            recipients = list(User.objects.filter(email=instance.email))

        if not recipients:
            return  # no user to notify

        # Build product list
        product_lines = []
        for item in instance.items.all():
            product_lines.append(f"  • {item.name} ×{item.qty} — ₹{item.line_total:,.0f}")
        product_summary = "\n".join(product_lines) if product_lines else "  (items unavailable)"

        for recipient in recipients:
            Notification.objects.create(
                user=recipient,
                notification_type='order_delivered',
                title=f'Order {instance.order_number} — Delivered Successfully!',
                message=(
                    f"Your order {instance.order_number} has been delivered successfully.\n\n"
                    f"Products delivered:\n{product_summary}\n\n"
                    f"Thank you for shopping with us!"
                ),
                related_order=instance,
            )
