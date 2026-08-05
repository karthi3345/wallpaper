"""Tests for the notification system — login/logout tracking and delivery notifications."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.urls import reverse

from shop.models import Notification, Order, OrderItem, Product, Category


class NotificationLoginLogoutTests(TestCase):
    """Verify that login and logout events create notifications."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )

    def test_login_creates_notification(self):
        """A successful login should create a 'login' notification."""
        self.client.login(username='testuser', password='testpass123')
        notif = Notification.objects.filter(user=self.user, notification_type='login')
        self.assertTrue(notif.exists(), 'Login notification was not created')
        self.assertEqual(notif.first().title, 'Login Successful')

    def test_logout_creates_notification(self):
        """A successful logout should create a 'logout' notification."""
        self.client.login(username='testuser', password='testpass123')
        # Clear the login notification so we can isolate the logout one
        Notification.objects.all().delete()
        self.client.logout()
        notif = Notification.objects.filter(user=self.user, notification_type='logout')
        self.assertTrue(notif.exists(), 'Logout notification was not created')
        self.assertEqual(notif.first().title, 'Logout Recorded')

    def test_multiple_logins_create_multiple_notifications(self):
        """Each login event should create a separate notification."""
        self.client.login(username='testuser', password='testpass123')
        self.client.logout()
        self.client.login(username='testuser', password='testpass123')
        login_count = Notification.objects.filter(user=self.user, notification_type='login').count()
        self.assertEqual(login_count, 2, 'Expected 2 login notifications')


class NotificationOrderDeliveryTests(TestCase):
    """Verify that order status → delivered creates a delivery notification."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer', email='buyer@example.com', password='buyerpass123'
        )
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            category=self.category,
            name='Luxury Wallpaper',
            slug='luxury-wallpaper',
            sku='SKU001',
            price=1999,
        )
        self.order = Order.objects.create(
            order_number='RWD-TEST001',
            customer_name='Buyer',
            email='buyer@example.com',
            phone='9999999999',
            address='123 Main St',
            city='Mumbai',
            pincode='400001',
            total=1999,
            status='confirmed',
            user=self.user,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            name='Luxury Wallpaper',
            price=1999,
            qty=2,
            unit='pc',
        )

    def test_delivered_status_creates_notification(self):
        """Changing order status to 'delivered' should create a delivery notification."""
        self.order.status = 'delivered'
        self.order.save()

        notif = Notification.objects.filter(
            user=self.user, notification_type='order_delivered'
        )
        self.assertTrue(notif.exists(), 'Delivery notification was not created')

    def test_delivered_notification_contains_product_names(self):
        """The delivery notification message should mention the product name."""
        self.order.status = 'delivered'
        self.order.save()

        notif = Notification.objects.get(
            user=self.user, notification_type='order_delivered'
        )
        self.assertIn('Luxury Wallpaper', notif.message)
        self.assertIn('RWD-TEST001', notif.message)
        self.assertIn('×2', notif.message)

    def test_non_delivered_status_does_not_create_notification(self):
        """Changing to a non-delivered status should NOT create a delivery notification."""
        self.order.status = 'shipped'
        self.order.save()

        notif = Notification.objects.filter(
            user=self.user, notification_type='order_delivered'
        )
        self.assertFalse(notif.exists(), 'Delivery notification should not be created for shipped status')

    def test_notification_linked_to_order(self):
        """The delivery notification should have a FK to the order."""
        self.order.status = 'delivered'
        self.order.save()

        notif = Notification.objects.get(
            user=self.user, notification_type='order_delivered'
        )
        self.assertEqual(notif.related_order, self.order)

    def test_delivered_notification_for_email_matched_user(self):
        """If order has no user FK but email matches a User, still notify."""
        order2 = Order.objects.create(
            order_number='RWD-TEST002',
            customer_name='Buyer',
            email='buyer@example.com',
            phone='9999999999',
            address='456 Oak St',
            city='Delhi',
            pincode='110001',
            total=500,
            status='confirmed',
            user=None,  # no user link
        )
        OrderItem.objects.create(
            order=order2,
            product=self.product,
            name='Luxury Wallpaper',
            price=500,
            qty=1,
            unit='pc',
        )
        order2.status = 'delivered'
        order2.save()

        notif = Notification.objects.filter(
            user=self.user, notification_type='order_delivered', related_order=order2
        )
        self.assertTrue(notif.exists(), 'Should notify user matched by email even without FK')


class NotificationModelTests(TestCase):
    """Test Notification model properties."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='u1', email='u1@test.com', password='pass123'
        )

    def test_icon_property(self):
        """Each notification type should return the right emoji icon."""
        for ntype, expected in [
            ('login', '🔑'),
            ('logout', '🚪'),
            ('order_delivered', '📦'),
            ('order_placed', '🛒'),
            ('order_shipped', '🚚'),
        ]:
            n = Notification.objects.create(
                user=self.user, notification_type=ntype,
                title='Test', message='Test'
            )
            self.assertEqual(n.icon, expected)

    def test_default_is_read_false(self):
        """New notifications should be unread by default."""
        n = Notification.objects.create(
            user=self.user, notification_type='login',
            title='Test', message='Test'
        )
        self.assertFalse(n.is_read)

    def test_str_representation(self):
        """__str__ should include username and title."""
        n = Notification.objects.create(
            user=self.user, notification_type='login',
            title='Login Successful', message='Test'
        )
        self.assertIn('u1', str(n))
        self.assertIn('Login Successful', str(n))


class NotificationViewTests(TestCase):
    """Test notification views — access control and mark-read."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='viewer', email='viewer@test.com', password='view123'
        )
        self.notif = Notification.objects.create(
            user=self.user, notification_type='login',
            title='Login Successful', message='You logged in.'
        )

    def test_notification_list_requires_login(self):
        """Unauthenticated users should be redirected to login."""
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_notification_list_shown_for_authenticated(self):
        """Logged-in users should see the notifications page."""
        self.client.login(username='viewer', password='view123')
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login Successful')

    def test_mark_notification_read(self):
        """Clicking mark-read should set is_read=True."""
        self.client.login(username='viewer', password='view123')
        self.assertFalse(self.notif.is_read)
        self.client.get(reverse('mark_notification_read', args=[self.notif.id]))
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_mark_all_read(self):
        """Mark-all-read should set all user's notifications to read."""
        Notification.objects.create(
            user=self.user, notification_type='login',
            title='Login 2', message='Test'
        )
        self.client.login(username='viewer', password='view123')
        self.client.post(reverse('mark_all_notifications_read'))
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_notification_isolated_per_user(self):
        """User A should not see User B's notifications."""
        user2 = User.objects.create_user(
            username='other', email='other@test.com', password='other123'
        )
        Notification.objects.create(
            user=user2, notification_type='login',
            title='Other Login', message='Secret'
        )
        self.client.login(username='viewer', password='view123')
        response = self.client.get(reverse('notification_list'))
        self.assertNotContains(response, 'Other Login')

    def test_notification_mark_read_uses_post(self):
        """Mark-all-read should require POST method."""
        self.client.login(username='viewer', password='view123')
        response = self.client.get(reverse('mark_all_notifications_read'))
        # GET should redirect (referer or list) but NOT mark as read
        self.notif.refresh_from_db()
        self.assertFalse(self.notif.is_read)
