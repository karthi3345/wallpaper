# PostgreSQL Persistent Data Fix

## Root Cause
PostgreSQL data directory at `/var/lib/postgresql/17/main` is **ephemeral** — wiped on every container restart. The old background service script reinstalled PostgreSQL from scratch each time, creating a fresh empty cluster. This caused "relation shop_product does not exist" errors after every container restart.

## Fix Applied
Moved PG data directory to `/home/coder/pgdata` (persistent volume).

### Background service (id 3575) — updated:
- Checks if `/home/coder/pgdata/PG_VERSION` exists before initializing
- Only runs `initdb` on first run; subsequent restarts reuse existing data
- Stops default cluster first to avoid port conflict
- Starts PG with `pg_ctl -D /home/coder/pgdata`

### Setup script — updated:
- Same persistent data dir logic
- Now also runs `seed_glass_mosaic` after `seed_demo`
- Both are idempotent (seed_demo checks if products exist, seed_glass_mosaic replaces the category's products)

### Env keys
- POSTGRES_* vars are in .env and used by Django via `os.environ.get('POSTGRES_*')`
- DB_* vars auto-resolve to MySQL but are ignored — Django settings.py prefers POSTGRES_* vars

## Verified
- 91 products (80 demo + 16 Glass Mosaic - 5 old glass mosaic replaced)
- Data survives procmgr restart of PG service
