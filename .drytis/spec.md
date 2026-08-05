# Red and Wine Decor — Spec

## Overview
Django + PostgreSQL e-commerce store for wallpapers, wall murals, and home decor. Inspired by redandwinedecor.in.

## Tech Stack
- **Backend:** Django 5.2 (Python 3.13)
- **Database:** PostgreSQL 17 (manually installed; NOT the auto-provisioned MySQL)
- **Frontend:** Django Templates + Tailwind CSS (CDN) + Alpine.js + Swiper.js
- **Font:** Jost (Google Fonts)
- **Accent:** Brown `#4A341D`
- **Currency:** INR (₹)

## Key Decisions
- PostgreSQL runs on localhost:5432, database `redwine_db`, user `redwine`.
- Tailwind via CDN (no build step needed) for rapid development.
- Session-based cart (no auth required to shop).
- Prices stored as DecimalField; formatted with ₹ symbol.
- Product images use external placeholder URLs from picsum/unsplash for demo.

## Categories
- Wall Murals: Heritage, European, Pichwai, Temple, Tropical, Chinoiseries, Leopard/Tiger, Ceiling, Kids & Nursery, Seamless, 3D Wallmural, Peacock
- Wallpaper Rolls: Luxury Series, Damask, Office, Floral, Abstract, Kids, Metallic, Texture
- Paintings/Wallart
- Glass Mosaic Tiles
- Home Decor
- Self Adhesive Wallpaper

## Rooms
Living Room, Bedroom, Dining Room, Hallway, Study Room, Kids Room, Bathroom

## Color Palette
Warm Neutrals, Earthy Browns, Cool Grays, Soft Blues, Sage & Greens
