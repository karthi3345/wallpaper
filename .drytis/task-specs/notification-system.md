# Notification System — Login/Logout Tracking + Delivery Notifications

## Overview
Add a persistent notification system that tracks:
1. **User login** — notification created on every successful login
2. **User logout** — notification created on every logout
3. **Order delivered** — notification when an order's status changes to `delivered`, listing the products successfully delivered

## Files to Change
- `shop/models.py` — Add `Notification` model + `user` FK to `Order`
- `shop/signals.py` — NEW: signal handlers for login/logout/order status change
- `shop/apps.py` — Wire up signals in `ready()`
- `shop/context_processors.py` — Add `notifications()` context processor
- `shop/views.py` — Add notification views (list, mark-read, mark-all-read)
- `shop/urls.py` — Add notification URL patterns
- `shop/admin.py` — Register Notification model
- `templates/partials/_header.html` — Add notification bell + dropdown
- `templates/partials/_notifications.html` — NEW: notification dropdown panel
- `templates/notifications.html` — NEW: full notifications list page
- `store/settings.py` — Add notifications context processor to TEMPLATES

## Acceptance Criteria
- [ ] `Notification` model exists with fields: user (FK), type, title, message, is_read, created_at, related_order (FK nullable)
- [ ] Order model gains nullable `user` FK (linked at checkout if user is authenticated)
- [ ] Login signal creates a notification with type `login`
- [ ] Logout signal creates a notification with type `logout`
- [ ] Order status change to `delivered` creates a notification with type `order_delivered` listing product names
- [ ] Notification bell appears in header with unread badge count
- [ ] Clicking bell shows dropdown with recent notifications
- [ ] Mark-as-read works (individual + mark-all)
- [ ] Full notifications page at `/notifications/`
- [ ] Unread count shown as badge on bell
- [ ] Context processor injects notifications globally
- [ ] Unit tests for signal handlers and notification creation
- [ ] Migration generated and applied

## Tests
- Signal creates login notification on `user_logged_in`
- Signal creates logout notification on `user_logged_out`
- Order status → `delivered` creates delivery notification with product names
- Unread count correct after mark-read
- Notification linked to correct user
