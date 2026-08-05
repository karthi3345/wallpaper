# Architecture

## Directory Structure
```
/workspace
├── manage.py
├── requirements.txt
├── store/                    # Django project package
│   ├── settings.py           # PostgreSQL config, templates, static, middleware
│   ├── urls.py               # URL routing
│   └── wsgi.py
├── shop/                     # Main app
│   ├── models.py             # Category, Product, Room, Color, Testimonial, Review, Order, OrderItem, NewsletterSubscriber
│   ├── views.py              # Home, catalog, product detail, cart, checkout
│   ├── urls.py               # Shop URL patterns
│   ├── admin.py              # Admin registrations
│   ├── context_processors.py # Cart count for global template access
│   ├── templatetags/
│   │   └── shop_tags.py      # price formatting filter
│   └── management/
│       └── commands/
│           └── seed_demo.py  # Demo data seeder
├── templates/
│   ├── base.html             # Head, header, footer, trust badges, scripts
│   ├── home.html             # Full homepage
│   ├── catalog.html          # Product listing with filters
│   ├── product_detail.html   # Single product
│   ├── cart.html             # Shopping cart
│   ├── checkout.html         # Checkout form + order summary
│   └── partials/             # Reusable partials
│       ├── _header.html
│       ├── _footer.html
│       ├── _product_card.html
│       └── _countdown.html
├── static/
│   ├── css/
│   │   └── custom.css        # Custom styles beyond Tailwind
│   ├── js/
│   │   └── main.js           # Alpine components, cart, countdown
│   └── images/               # Static images
└── tests/
    ├── test_cart.py          # Cart logic unit tests
    ├── test_catalog.py       # Catalog filtering integration tests
    └── test_checkout.py      # Checkout flow integration tests
```

## Data Flow
1. **Homepage:** Queries featured/best_seller/latest products, categories, rooms, colors, testimonials → renders sections
2. **Catalog:** Filters products by category slug, room, color, price range → paginated results
3. **Product Detail:** Product by slug + related products in same category
4. **Cart:** Session-based — `request.session['cart'] = {product_id: qty}`
5. **Checkout:** Validates form → creates Order + OrderItems → clears cart

## Routing
- `/` — Homepage
- `/shop/` — All products
- `/category/<slug>/` — Products by category
- `/product/<slug>/` — Product detail
- `/cart/` — Cart view
- `/cart/add/<int:product_id>/` — Add to cart
- `/cart/remove/<int:product_id>/` — Remove from cart
- `/cart/update/<int:product_id>/` — Update quantity
- `/checkout/` — Checkout form
- `/newsletter/` — Newsletter signup (POST)
