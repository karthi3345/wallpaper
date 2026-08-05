# PostgreSQL Startup Race Condition — Fixed

## Root Cause
The background service script (id 3575) and setup script both checked for
`/home/coder/pgdata/PG_VERSION` **as the `coder` user**. But the pgdata directory
is owned by `postgres` with mode `drwx------` (700), so `coder` gets permission
denied when trying to stat files inside it.

The `if [ ! -f ... ]` test silently fails (permission denied → file not found),
so the script thinks it needs to run `initdb` on every restart. `initdb` then
fails with "directory exists but is not empty" → procmgr marks service as
STOPPED → Django gets "Connection refused" on port 5432.

## Fix Applied
Both the background service script and setup script now use **`sudo test -f`**
to check for PG_VERSION, which reads as root and sees the actual file state.

Additional robustness:
- Checks `pg_ctl status` before starting (avoids "already running" errors)
- Removes stale `postmaster.pid` from unclean shutdowns (container pause/crash)
- Uses `sudo rm -rf` + clean mkdir before initdb (never partially-initialized)
- Ends with `while true; do sleep 60; done` to keep the procmgr process alive

## Timeline
- First crash: corrupt data dir (partial initdb with missing pg_control)
- Second crash: same permission race on PG_VERSION check
- Fix: updated bg service 3575 + setup script to use `sudo test -f`

## Verified
- procmgr restart → service RUNNING, 96 products intact, HTTP 200
