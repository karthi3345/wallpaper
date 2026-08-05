# Geographic Wallpaper Catalog — "Shop by Country"

## Goal
Add a new catalog section where users browse wallpapers by **Country → State/Region → City**. Each location showcases famous wallpapers associated with that area. This creates a geographic discovery layer on top of the existing category/room/color facets.

## Models (shop/models.py)

### Country
- `name` (CharField 100)
- `slug` (SlugField unique)
- `image` (URLField — hero/flag image)
- `description` (TextField blank)
- `sort_order` (Int, default 0)
- `is_active` (Bool, default True)

### Region (State/Province within a Country)
- `country` (FK → Country, related_name="regions")
- `name` (CharField 100)
- `slug` (SlugField unique)
- `image` (URLField blank)
- `description` (TextField blank)
- `sort_order` (Int, default 0)
- `is_active` (Bool, default True)

### City (City/Town within a Region)
- `region` (FK → Region, related_name="cities")
- `name` (CharField 100)
- `slug` (SlugField unique)
- `image` (URLField blank)
- `description` (TextField blank)
- `sort_order` (Int, default 0)
- `is_active` (Bool, default True)
- `featured` (Bool, default False)

### Product changes
- Add M2M `cities` to Product (related_name="city_products") — a wallpaper can be associated with multiple cities.

## Views & URLs
- `/countries/` → countries (list all active countries)
- `/countries/<country_slug>/` → country_detail (regions + featured wallpapers)
- `/countries/<country_slug>/<region_slug>/` → region_detail (cities + wallpapers)
- `/countries/<country_slug>/<region_slug>/<city_slug>/` → city_detail (wallpaper grid)

## Homepage
New "Shop by Country" section after "Shop by Category".

## Header
Add "Countries" link in desktop nav and mobile menu.

## Seed Data
India, Italy, France, England, USA, Japan — each with states/regions, major cities, and product associations.

## Acceptance Criteria
- [ ] Country/Region/City models exist and migration applies cleanly
- [ ] Admin interface allows CRUD for all three models
- [ ] `/countries/` page renders with country cards
- [ ] Country detail shows regions + featured wallpapers
- [ ] Region detail shows cities + wallpapers
- [ ] City detail shows wallpaper grid
- [ ] Homepage has "Shop by Country" section
- [ ] Header nav has "Countries" link
- [ ] Seed command populates data without errors
- [ ] All pages responsive
- [ ] No console errors
