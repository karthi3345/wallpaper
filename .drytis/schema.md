# Schema

## Tables

### category
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| name | CharField(100) | |
| slug | SlugField unique | |
| parent | FK self nullable | For subcategories |
| image | URLField | Category image |
| sort_order | IntegerField | Display order |
| is_active | BooleanField | |

### product
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| category | FK category | |
| name | CharField(200) | |
| slug | SlugField unique | |
| sku | CharField(50) unique | |
| description | TextField | |
| price | DecimalField(10,2) | INR |
| unit | CharField(20) | 'pc' or 'sqft' |
| images | JSONField | List of image URLs |
| featured | BooleanField | Homepage spotlight |
| best_seller | BooleanField | Best sellers section |
| is_latest | BooleanField | Latest arrivals |
| status | CharField | active/inactive |
| sort_order | IntegerField | |
| created_at | DateTimeField | |

### room
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| name | CharField(100) | |
| slug | SlugField unique | |
| image | URLField | |
| sort_order | IntegerField | |

### color
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| name | CharField(100) | |
| slug | SlugField unique | |
| hex_code | CharField(7) | #RRGGBB |
| image | URLField | |
| sort_order | IntegerField | |

### product_room (M2M)
- product_id FK
- room_id FK

### product_color (M2M
- product_id FK
- color_id FK

### testimonial
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| author | CharField(100) | |
| content | TextField | |
| rating | IntegerField | 1-5 |
| image | URLField | |
| sort_order | IntegerField | |

### review
| Column | Type | Notes |
|--------|------|.md |
| id | AutoField PK | |
| product | FK product | |
| author | CharField(100) | |
| rating | IntegerField | 1-5 |
| content | TextField | |
| created_at | DateTimeField | |

### order
| Column | Type | Notes |
|--------|------|-------|
| id | AutoField PK | |
| order_number | CharField(20) unique | Auto-generated |
| customer_name | CharField(200) | |
| email | EmailField | |
| phone | CharField(20) | |
| address | TextField | |
| city | CharField(100) | |
| pincode | CharField(10) | |
| total | DecimalField(10,2) | |
| status | CharField | pending/confirmed/shipped/delivered |
| payment_status | CharField | unpaid/paid |
| created_at | DateTimeField | |

### order_item
| Column | Type | Notes |
|--------|------|-------|---------------|
| id | AutoField PK | |
| order | FK order | cascade |
| product | FK product | set_null |
| name | CharField(200) | Snapshot |
| price | DecimalField(10,2) | Snapshot |
| qty | IntegerField | |
| unit | CharField(20) | Snapshot |

### newsletter_subscriber
| Column | Type | |
|--------|------|---|
| id | AutoField PK | |
| email | EmailField unique | |
| created_at | DateTimeField | |
