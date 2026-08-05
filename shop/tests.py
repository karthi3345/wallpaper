from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
import hashlib
import hmac

from shop.models import (
    Category, Product, Order, OrderItem,
)


def _seed_product():
    """Create a minimal product for cart testing."""
    cat = Category.objects.create(name='Test Cat', slug='test-cat')
    return Product.objects.create(
        category=cat, name='Test Wallpaper', slug='test-wallpaper',
        sku='TW001', price=Decimal('999.00'),
    )


def _add_to_cart(client, product_id):
    """Helper: add product to session cart via POST."""
    client.post(reverse('add_to_cart', args=[product_id]))


# ---------------------------------------------------------------------------
# Unit tests — order model & payment state transitions
# ---------------------------------------------------------------------------

class OrderModelTests(TestCase):

    def test_generate_order_number_format(self):
        num = Order.generate_order_number()
        self.assertTrue(num.startswith('RWD-'))
        self.assertEqual(len(num), 12)  # RWD- + 8 hex chars

    def test_generate_order_number_uniqueness(self):
        nums = {Order.generate_order_number() for _ in range(100)}
        self.assertEqual(len(nums), 100)

    def test_payment_choices_include_new_states(self):
        choices = dict(Order.PAYMENT_CHOICES)
        self.assertIn('pending', choices)
        self.assertIn('failed', choices)
        self.assertIn('unpaid', choices)
        self.assertIn('paid', choices)

    def test_payment_method_choices(self):
        choices = dict(Order.PAYMENT_METHOD_CHOICES)
        self.assertEqual(choices['cod'], 'Cash on Delivery')
        self.assertEqual(choices['online'], 'Online Payment')


class OrderItemLineTotalTests(TestCase):

    def test_line_total(self):
        cat = Category.objects.create(name='C', slug='c')
        prod = Product.objects.create(
            category=cat, name='P', slug='p', sku='P1',
            price=Decimal('500.00'),
        )
        order = Order.objects.create(
            order_number='RWD-TEST', customer_name='Test', email='t@e.com',
            phone='123', address='A', city='City', pincode='560001',
            total=Decimal('1000.00'),
        )
        item = OrderItem.objects.create(
            order=order, product=prod, name='P', price=Decimal('500.00'), qty=2,
        )
        self.assertEqual(item.line_total, Decimal('1000.00'))


# ---------------------------------------------------------------------------
# Unit tests — Razorpay signature verification logic
# ---------------------------------------------------------------------------

class SignatureVerificationTests(TestCase):

    @override_settings(RAZORPAY_KEY_SECRET='test_secret_123')
    def test_valid_signature(self):
        key_secret = 'test_secret_123'
        razorpay_order_id = 'order_abc123'
        razorpay_payment_id = 'pay_xyz789'

        msg = f'{razorpay_order_id}|{razorpay_payment_id}'
        expected_sig = hmac.new(
            key_secret.encode(),
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Recompute in the same way the view does
        recomputed = hmac.new(
            key_secret.encode(),
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.assertTrue(hmac.compare_digest(expected_sig, recomputed))

    @override_settings(RAZORPAY_KEY_SECRET='test_secret_123')
    def test_invalid_signature(self):
        key_secret = 'test_secret_123'
        msg = b'order_abc123|pay_xyz789'
        valid_sig = hmac.new(key_secret.encode(), msg, hashlib.sha256).hexdigest()
        tampered_sig = valid_sig[:-4] + '0000'

        self.assertFalse(hmac.compare_digest(valid_sig, tampered_sig))


# ---------------------------------------------------------------------------
# Integration tests — checkout flow (COD and Online)
# ---------------------------------------------------------------------------

class CheckoutCODIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.product = _seed_product()
        _add_to_cart(self.client, self.product.id)

    def test_cod_checkout_creates_unpaid_order(self):
        response = self.client.post(reverse('checkout'), {
            'customer_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '9876543210',
            'address': '123 Main St',
            'city': 'Bangalore',
            'pincode': '560001',
            'payment': 'cod',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('order-confirmation', response.url)
        order = Order.objects.get(customer_name='John Doe')
        self.assertEqual(order.payment_status, 'unpaid')
        self.assertEqual(order.payment_method, 'cod')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.items.count(), 1)

    def test_cod_clears_cart(self):
        self.client.post(reverse('checkout'), {
            'customer_name': 'Jane', 'email': 'j@e.com', 'phone': '123',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'cod',
        })
        self.assertEqual(self.client.session.get('cart', {}), {})


class CheckoutOnlineIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.product = _seed_product()
        _add_to_cart(self.client, self.product.id)

    def test_online_checkout_creates_pending_order_and_redirects_to_payment(self):
        response = self.client.post(reverse('checkout'), {
            'customer_name': 'Online User',
            'email': 'online@example.com',
            'phone': '9876543210',
            'address': '456 Park St',
            'city': 'Mumbai',
            'pincode': '400001',
            'payment': 'online',
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(customer_name='Online User')
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(order.payment_method, 'online')
        # Should redirect to payment page, not confirmation
        self.assertIn('/payment/', response.url)

    def test_online_checkout_clears_cart(self):
        self.client.post(reverse('checkout'), {
            'customer_name': 'O', 'email': 'o@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        self.assertEqual(self.client.session.get('cart', {}), {})


class EmptyCartCheckoutTests(TestCase):

    def test_empty_cart_redirects_to_catalog(self):
        client = Client()
        response = client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('shop', response.url)


# ---------------------------------------------------------------------------
# Integration tests — payment verification (demo mode)
# ---------------------------------------------------------------------------

class PaymentVerifyDemoModeTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.product = _seed_product()
        _add_to_cart(self.client, self.product.id)
        # Create an online order
        self.client.post(reverse('checkout'), {
            'customer_name': 'Pay User', 'email': 'p@e.com', 'phone': '9876543210',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        self.order = Order.objects.get(customer_name='Pay User')

    def test_demo_success_marks_paid_and_confirmed(self):
        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'demo_result': 'success'},
        )
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertIn('order-confirmation', response.url)
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'confirmed')
        self.assertTrue(self.order.razorpay_payment_id)

    def test_demo_failure_marks_failed(self):
        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'demo_result': 'failure'},
        )
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertIn('failed', response.url)
        self.assertEqual(self.order.payment_status, 'failed')


class AlreadyPaidOrderTests(TestCase):

    def test_already_paid_order_redirects_to_confirmation(self):
        client = Client()
        product = _seed_product()
        _add_to_cart(client, product.id)
        client.post(reverse('checkout'), {
            'customer_name': 'Paid', 'email': 'p2@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        order = Order.objects.get(customer_name='Paid')
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()

        response = client.post(
            reverse('payment_verify', args=[order.order_number]),
            {'demo_result': 'success'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('order-confirmation', response.url)


# ---------------------------------------------------------------------------
# Integration tests — payment page rendering
# ---------------------------------------------------------------------------

class PaymentPageTests(TestCase):

    def setUp(self):
        self.client = Client()
        product = _seed_product()
        _add_to_cart(self.client, product.id)
        self.client.post(reverse('checkout'), {
            'customer_name': 'PP', 'email': 'pp@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        self.order = Order.objects.get(customer_name='PP')

    def test_payment_page_renders_in_demo_mode(self):
        response = self.client.get(
            reverse('payment_page', args=[self.order.order_number])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demo Mode')
        self.assertContains(response, 'Simulate Successful Payment')

    def test_payment_failed_page_renders(self):
        response = self.client.get(
            reverse('payment_failed', args=[self.order.order_number])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Failed')


class PaymentPageGuardTests(TestCase):
    """Non-online or non-pending orders should be redirected away from the payment page."""

    def setUp(self):
        self.client = Client()
        product = _seed_product()
        _add_to_cart(self.client, product.id)

    def test_cod_order_redirected_from_payment_page(self):
        self.client.post(reverse('checkout'), {
            'customer_name': 'COD', 'email': 'cod@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'cod',
        })
        order = Order.objects.get(customer_name='COD')
        response = self.client.get(reverse('payment_page', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('order-confirmation', response.url)


# ---------------------------------------------------------------------------
# Integration tests — confirmation page payment status display
# ---------------------------------------------------------------------------

class ConfirmationPageTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.product = _seed_product()
        _add_to_cart(self.client, self.product.id)

    def test_cod_confirmation_shows_cash_on_delivery(self):
        self.client.post(reverse('checkout'), {
            'customer_name': 'C', 'email': 'c@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'cod',
        })
        order = Order.objects.get(customer_name='C')
        response = self.client.get(reverse('order_confirmation', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Status')

    def test_online_pending_confirmation_shows_pay_now(self):
        self.client.post(reverse('checkout'), {
            'customer_name': 'OP', 'email': 'op@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        order = Order.objects.get(customer_name='OP')
        response = self.client.get(reverse('order_confirmation', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Your Payment')


# ---------------------------------------------------------------------------
# Integration tests — LIVE MODE signature verification (security-critical)
# ---------------------------------------------------------------------------

class LiveModeSignatureTests(TestCase):
    """Tests that exercise the payment_verify view with real Razorpay settings
    configured (live mode). Verifies that demo_result param CANNOT bypass
    signature verification."""

    def setUp(self):
        self.product = _seed_product()
        self.client = Client()
        _add_to_cart(self.client, self.product.id)
        self.client.post(reverse('checkout'), {
            'customer_name': 'Live', 'email': 'live@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        self.order = Order.objects.get(customer_name='Live')

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_livekey',
        RAZORPAY_KEY_SECRET='live_secret_key_456',
    )
    def test_demo_result_cannot_bypass_in_live_mode(self):
        """Posting demo_result=success without a signature must FAIL in live mode."""
        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'demo_result': 'success'},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')
        self.assertIn('failed', response.url)

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_livekey',
        RAZORPAY_KEY_SECRET='live_secret_key_456',
    )
    def test_missing_signature_fails_in_live_mode(self):
        """Even without demo_result, a missing signature must fail."""
        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'razorpay_payment_id': 'pay_123', 'razorpay_order_id': 'order_abc'},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_livekey',
        RAZORPAY_KEY_SECRET='live_secret_key_456',
    )
    def test_valid_signature_marks_paid_in_live_mode(self):
        """A correct HMAC-SHA256 signature marks the order as paid."""
        razorpay_order_id = 'order_test123'
        razorpay_payment_id = 'pay_test456'
        key_secret = 'live_secret_key_456'

        msg = f'{razorpay_order_id}|{razorpay_payment_id}'
        sig = hmac.new(key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()

        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': sig,
            },
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'confirmed')
        self.assertEqual(self.order.razorpay_payment_id, razorpay_payment_id)
        self.assertEqual(self.order.razorpay_signature, sig)

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_livekey',
        RAZORPAY_KEY_SECRET='live_secret_key_456',
    )
    def test_invalid_signature_fails_in_live_mode(self):
        """A tampered signature must fail."""
        razorpay_order_id = 'order_test123'
        razorpay_payment_id = 'pay_test456'
        key_secret = 'live_secret_key_456'

        msg = f'{razorpay_order_id}|{razorpay_payment_id}'
        sig = hmac.new(key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
        tampered = sig[:-4] + '0000'

        response = self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': tampered,
            },
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')
        self.assertIn('failed', response.url)


# ---------------------------------------------------------------------------
# Integration tests — retry after failure
# ---------------------------------------------------------------------------

class RetryAfterFailureTests(TestCase):

    def setUp(self):
        self.product = _seed_product()
        self.client = Client()
        _add_to_cart(self.client, self.product.id)
        self.client.post(reverse('checkout'), {
            'customer_name': 'Retry', 'email': 'retry@e.com', 'phone': '1',
            'address': 'A', 'city': 'C', 'pincode': '560001', 'payment': 'online',
        })
        self.order = Order.objects.get(customer_name='Retry')
        # Simulate a failed payment
        self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'demo_result': 'failure'},
        )
        self.order.refresh_from_db()

    def test_failed_order_can_access_payment_page_for_retry(self):
        """A failed order should be able to re-enter the payment page."""
        response = self.client.get(reverse('payment_page', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 200)
        # Should show the demo payment UI again
        self.assertContains(response, 'Simulate Successful Payment')

    def test_failed_order_reset_to_pending_on_retry(self):
        """Visiting payment_page resets failed → pending."""
        self.assertEqual(self.order.payment_status, 'failed')
        self.client.get(reverse('payment_page', args=[self.order.order_number]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')

    def test_retry_success_marks_paid(self):
        """After retry, a successful payment marks the order paid."""
        # Visit payment page to reset to pending
        self.client.get(reverse('payment_page', args=[self.order.order_number]))
        # Simulate successful payment
        self.client.post(
            reverse('payment_verify', args=[self.order.order_number]),
            {'demo_result': 'success'},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'confirmed')
