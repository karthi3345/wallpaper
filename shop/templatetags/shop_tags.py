from django import template

register = template.Library()


@register.filter
def inr(value):
    """Format a Decimal as INR: ₹1,299"""
    try:
        return f'₹{int(value):,}'
    except (ValueError, TypeError):
        return value


@register.filter
def inr_decimal(value):
    """Format a Decimal as INR with no thousands sep for sqft rates: ₹85/sqft"""
    try:
        return f'₹{int(value)}'
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def unit_label(unit):
    if unit == 'sqft':
        return '/sqft'
    return ''
