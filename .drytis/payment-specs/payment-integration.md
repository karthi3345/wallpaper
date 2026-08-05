# Payment Integration — Razorpay

## Overview
Add Razorpay payment gateway to the Red and Wine Decor e-commerce store. Users can choose between Cash on Delivery (existing) and Online Payment (new). Online payments use Razorpay Checkout.js for UPI, cards, netbanking, and wallets. Includes a demo/test mode so the integration is fully testable without real Razorpay credentials.

## Tech
- **Gateway:** Razorpay (Python SDK + Checkout.js)
- **Currency:** INR (amounts in paise for API calls)
- **Flow:** Server creates Razorpay Order → Razorpay Checkout.js modal → signature verification on callback → order marked paid

## Files to Change
1. `shop/models.py` — Extend `Order` model with payment fields
2. `shop/views.py` — Modify checkout, add payment_page + payment_verify + payment_failed views
3. `shop/urls.py` — Add payment routes
4. `shop/admin.py` — Show new payment fields
5. `store/settings.py` — Razorpay config
6. `templates/checkout.html` — Enable online payment radio
7. `templates/payment.html` — NEW: Razorpay checkout page
8. `templates/order_confirmation.html` — Show payment status, Pay Now for pending
9. `templates/payment_failed.html` — NEW: payment failure page
10. `requirements.txt` — Add razorpay SDK
11. Migration for new model fields
12. Backend env keys: RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

## Database Schema Changes
**Order** — new fields:
- `payment_method` CharField(20), default='cod' — 'cod' | 'online'
- `razorpay_order_id` CharField(100), blank — gateway order reference
- `razorpay_payment_id` CharField(100), blank — gateway payment reference
- `razorpay_signature` CharField(200), blank — signature for verification

PAYMENT_CHOICES expanded: unpaid, pending, paid, failed

## Payment Flow
### COD (unchanged)
checkout POST → create order (unpaid) → clear cart → confirmation page

### Online Payment
1. checkout POST (payment=online) → create order (payment_status=pending, payment_method=online) → clear cart → redirect to payment_page
2. payment_page: server creates Razorpay Order via API → render Razorpay Checkout.js
3. User pays in Razorpay modal → JS handler sends razorpay_payment_id + razorpay_order_id + razorpay_signature to payment_verify
4. payment_verify: verify HMAC-SHA256 signature → if valid: mark paid + confirmed → redirect to confirmation; if invalid: mark failed → redirect to payment_failed
5. If Razorpay keys not configured: demo mode with simulate success/failure buttons

## Acceptance Criteria
- [ ] Order model has razorpay_order_id, razorpay_payment_id, razorpay_signature, payment_method fields
- [ ] PAYMENT_CHOICES includes pending and failed states
- [ ] Migration applies cleanly
- [ ] Checkout page has functional Online Payment radio option (not disabled)
- [ ] Selecting COD creates order with payment_status=unpaid and redirects to confirmation
- [ ] Selecting Online Payment creates order with payment_status=pending and redirects to payment page
- [ ] Payment page renders Razorpay checkout (or demo mode without keys)
- [ ] Demo mode: simulate success marks order as paid + confirmed
- [ ] Demo mode: simulate failure marks order as failed and shows failure page
- [ ] Order confirmation page shows payment status
- [ ] Order confirmation page shows "Pay Now" button for pending orders
- [ ] Admin shows new payment fields (razorpay_order_id, razorpay_payment_id as readonly)
- [ ] Razorpay credentials are stored as env keys, never hardcoded
- [ ] Signature verification uses HMAC-SHA256
- [ ] Cart is cleared only once (before payment, after order creation)

## Tests
### Unit Tests
- Razorpay order creation (amount in paise)
- Signature verification (valid + invalid)
- Order state transitions (pending → paid, pending → failed)

### Integration Tests
- COD checkout creates unpaid order
- Online checkout creates pending order + redirects to payment
- Payment verify callback with valid signature marks paid
- Payment verify callback with invalid signature marks failed
- Payment failed page renders

### Edge Cases
- Empty cart cannot reach checkout
- Already-paid order cannot be re-verified
- Razorpay keys missing → demo mode active
