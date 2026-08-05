# Patterns

## Naming
- Models: PascalCase singular (Category, Product)
- Views: lowercase with underscores (product_detail, add_to_cart)
- Templates: lowercase with underscores, snake_case
- URLs: lowercase with hyphens for slugs, underscores for routes
- CSS classes: Tailwind utility classes + custom classes in custom.css

## Models
- Always define `__str__` returning name or title
- Add `Meta` class with `ordering` where appropriate
- Use `slug` fields for categories, products, rooms, colors
- Use `DecimalField` for prices (max_digits=10, decimal_places=2)
- Use JSONField for product images list

## Views
- Class-based ListView for catalog, DetailView for product detail
- Function-based for cart/checkout/home (simpler session logic)
- Always pass cart context via context processor

## Templates
- `{% extends 'base.html' %}` for all pages
- `{% block content %}` for page content
- Use `{% load shop_tags %}` for custom filters
- Alpine.js for interactivity (x-data, x-show, @click)
- Swiper.js for carousels
- Tailwind CSS for styling

## Error Handling
- `get_object_or_404` for single object lookups
- Django messages framework for cart/checkout feedback
- Form validation in checkout view

## Testing
- Unit tests in /workspace/tests/
- Use Django TestCase with test database
- Test cart logic, catalog filtering, checkout flow
- Name tests: test_<behavior>
