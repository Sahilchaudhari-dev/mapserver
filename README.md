# Mapserver

A self-hosted OpenStreetMap tile server with custom boundary overlays, built on Mapnik/renderd/mod_tile, PostGIS, and a FastAPI backend.

Currently serves map data for India (base import), with Pakistan and Xinjiang appended, plus custom boundary line overlays rendered on top via a separate API.

## Architecture

```
Browser (Leaflet map)
   |
   v
FastAPI backend (uvicorn, app/backend/app)
   |  - /api/tiles/{z}/{x}/{y}.png  -> proxies to Apache/mod_tile
   |  - /api/boundaries/{region}     -> serves boundary GeoJSON from PostGIS
   v
Apache + mod_tile + renderd
   |  - renders tiles via Mapnik using openstreetmap-carto style
   v
PostGIS (geodb)
   - planet_osm_point / line / polygon (from osm2pgsql imports)
   - boundaries table (custom overlay geometries)
```

## Prerequisites

- WSL2 (Ubuntu) or native Linux
- PostgreSQL + PostGIS
- Python 3.10+
- Apache2, mod_tile, renderd, mapnik
- osm2pgsql
- osmium-tool (for verifying `.osm.pbf` downloads)

## Setup

### 1. Clone this repo

```bash
git clone https://github.com/<your-username>/mapserver.git
cd mapserver
```

### 2. Clone openstreetmap-carto (not bundled in this repo)

```bash
git clone https://github.com/gravitystorm/openstreetmap-carto.git
```

### 3. Set up the database

```bash
sudo -u postgres createdb geodb
sudo -u postgres psql -d geodb -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -d geodb -c "CREATE EXTENSION hstore;"
```

Create a DB user matching what you'll put in `.env` and `mapnik.xml` (see step 5).

### 4. Import OSM data

Download region extracts from [Geofabrik](https://download.geofabrik.de/), verify, then import.

```bash
# Verify a downloaded extract before importing
osmium fileinfo data/<region>-latest.osm.pbf

# First import (creates tables)
osm2pgsql -O flex -S openstreetmap-carto/openstreetmap-carto-flex.lua \
  -d geodb -U geouser -H localhost -P 5432 \
  --slim -C 4000 --number-processes 4 \
  --flat-nodes data/flat-nodes.bin \
  data/india-latest.osm.pbf

# Subsequent regions: use --append to add without touching existing data
PGPASSWORD=<your_password> osm2pgsql -O flex -S openstreetmap-carto/openstreetmap-carto-flex.lua \
  -d geodb -U geouser -H localhost -P 5432 \
  --slim --append -C 4000 --number-processes 4 \
  --flat-nodes data/flat-nodes.bin \
  data/pakistan-latest.osm.pbf
```

### 5. Configure mapnik.xml

`mapnik.xml` is **not committed** to this repo (it contains DB credentials). Generate it from openstreetmap-carto and edit the Postgres connection parameters (`dbname`, `host`, `user`, `password`) to match your local setup:

```bash
cd openstreetmap-carto
# follow openstreetmap-carto's own instructions to generate mapnik.xml via carto/project.mml
```

### 6. Configure renderd and Apache

Copy the sample configs from `configs/` to their system locations and adjust paths:

```bash
sudo cp configs/renderd.conf /etc/renderd.conf
sudo cp configs/mod_tile.conf /etc/apache2/mods-available/mod_tile.conf
sudo cp configs/000-default.conf /etc/apache2/sites-available/000-default.conf
```

Edit `/etc/renderd.conf` — under your map's `[name]` section, set `XML` to the full path of your `mapnik.xml`.

Restart services:

```bash
sudo systemctl restart renderd
sudo systemctl restart apache2
```

### 7. Backend setup

```bash
cd app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

Copy `.env.example` (if present) to `.env` and fill in your DB credentials and any other config values used by `app/backend/app/config.py`.

Run the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

`--host 0.0.0.0` is required if you want the server reachable from other machines on your network, not just localhost.

## Adding a new region

1. Download the region's extract from Geofabrik, verify with `osmium fileinfo`.
2. Import with `osm2pgsql ... --append` (never omit `--append` after the first region, or you'll wipe existing data).
3. If you want a custom boundary overlay for it, pull the boundary via Overpass API using its OSM relation ID, insert into the `boundaries` table, and it'll be served automatically at `/api/boundaries/<name>`.
4. Force-render the new region's tiles so cached blank tiles from before the import don't linger:
   ```bash
   render_list -a -z 0 -Z 10 -n 4 -m <style_name>
   ```
   Increase `-Z` cautiously — tile counts grow ~4x per zoom level, and rendering globally past zoom ~12 can consume significant disk space. Prefer a bounding-box-restricted render for high zoom levels on a specific region.

## Accessing from other machines on your network (WSL2)

WSL2's internal IP is only reachable from the Windows host. To expose the server to other devices on your LAN:

```powershell
# Run in Windows PowerShell as Administrator
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=<WSL_INTERNAL_IP>
New-NetFirewallRule -DisplayName "Mapserver 8080" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

Other devices connect via your **Windows machine's LAN IP** (`ipconfig` → IPv4 Address), not the WSL internal IP.

WSL2's internal IP can change on restart — if the connection stops working after a reboot, re-run the `portproxy` command with the new IP (check via `wsl hostname -I` or `ip addr` inside WSL).

## Troubleshooting

- **Blank tiles (200 OK, tiny PNG) over a specific region**: usually a stale render cache from before that region's data was imported, or (less commonly) a broken `mapnik.xml` causing renderd to silently serve empty tiles. Check `journalctl -u renderd -n 50` for load errors first.
- **`renderd` fails with "socket bind failed"**: on WSL, `/run/renderd/` can get wiped on restart since `/run` is tmpfs. Recreate it: `sudo mkdir -p /run/renderd && sudo chown $(whoami):$(whoami) /run/renderd`.
- **`render_list` says "No map for: X"**: the `-m` style name must match the `[name]` section header in `/etc/renderd.conf`, not a guess.
- **Labels showing in local script (Urdu/Chinese) instead of English**: OSM stores translated names inside the `tags` column (flex import), not as a separate top-level column. Reference `tags->'name:en'` in layer queries, not `"name:en"` directly — and only on queries selecting directly from `planet_osm_*` tables, not on outer queries wrapping an already-aliased subquery.

## Project structure

```
mapserver/
├── app/
│   ├── backend/
│   │   └── app/
│   │       ├── main.py
│   │       ├── config.py
│   │       ├── database.py
│   │       ├── routers/
│   │       │   ├── tiles.py         # proxies tile requests to Apache/mod_tile
│   │       │   ├── boundaries.py    # serves custom boundary overlays
│   │       │   ├── map_init.py
│   │       │   └── health.py
│   │       ├── services/
│   │       │   └── boundary_service.py
│   │       └── static/
│   │           └── index.html       # Leaflet frontend
│   └── requirements.txt
├── configs/
│   ├── renderd.conf
│   ├── mod_tile.conf
│   └── 000-default.conf
└── .gitignore
```