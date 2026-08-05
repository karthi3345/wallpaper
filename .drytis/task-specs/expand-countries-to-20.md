# Task: Expand Countries Catalog to 20 Countries

## Goal
The geographic catalog (Country → Region → City → Wallpaper) is fully implemented with 6 countries. Expand the seed data to include **20 countries total** with regions/states, cities/towns, and curated wallpaper associations.

## Current 6 Countries (keep as-is)
1. India, 2. Italy, 3. France, 4. England, 5. United States, 6. Japan

## 14 New Countries to Add
7. Spain, 8. Germany, 9. Morocco, 10. Turkey, 11. China, 12. UAE,
13. Brazil, 14. Australia, 15. Netherlands, 16. Thailand, 17. Greece,
18. Mexico, 19. Russia, 20. Egypt

## Each country needs:
- Name, slug, hero image (Unsplash), description
- 2-4 regions/states (name, slug, image, description)
- Each region: 2-5 cities/towns (name, slug, image optional, description, featured flag)

## Acceptance Criteria
- [ ] `seed_geo.py` COUNTRIES list has exactly 20 entries
- [ ] `python manage.py seed_geo` runs without errors (idempotent via get_or_create)
- [ ] `/countries/` page shows all 20 country cards
- [ ] Country detail pages load for all 20 countries
- [ ] Products are re-associated across all cities (existing random seed logic)
- [ ] Homepage "Shop by Country" section still works (showing 6 featured)
