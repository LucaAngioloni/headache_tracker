# Headache Tracker

Personal multi-user headache diary: medicines, episodes with doses, triggers, calendar, stats.

## Installation and Usage

### Prerequisites

- **Docker** with Docker Compose v2 (included with Docker Desktop on macOS/Windows, or `docker-compose-plugin` on Linux).
- (Optional) `just`, the command runner used throughout this guide. The equivalent plain `docker compose ...` commands are shown where useful; install [just](https://github.com/casey/just) or fall back to raw `docker compose`.

### Option A — Production (prebuilt images)

Uses the prebuilt images already published to GHCR, with no local build. This is the recommended way to run the app.

1. Get the production compose file `docker-compose.yml` (from the repo root or by cloning):

   ```bash
   curl -O https://raw.githubusercontent.com/lucaangioloni/headache_tracker/main/docker-compose.yml
   ```

2. Create the environment file from the example and review it:

   ```bash
   curl -O https://raw.githubusercontent.com/lucaangioloni/headache_tracker/main/.env.example
   cp .env.example .env
   ```

   At minimum set a strong `DJANGO_SECRET_KEY` and your `DOMAIN` before going live.

3. Run the Django one-time setup:

   ```bash
   docker compose pull
   docker compose run backend python manage.py migrate
   docker compose run backend python manage.py collectstatic
   docker compose run backend python manage.py createsuperuser
   ```

   Or with `just` (and `COMPOSE_FILE` set to `docker-compose.yml`):

   ```bash
   COMPOSE_FILE=docker-compose.yml just pull
   COMPOSE_FILE=docker-compose.yml just migrate
   COMPOSE_FILE=docker-compose.yml just collectstatic
   COMPOSE_FILE=docker-compose.yml just createsuperuser
   ```

4. Start the stack:

   ```bash
   docker compose up
   ```

   Or with `just`:

   ```bash
   COMPOSE_FILE=docker-compose.yml just up
   ```

   Or in detached mode: `docker compose up -d` or`COMPOSE_FILE=docker-compose.yml just upd`.

Open <http://localhost> (or your `DOMAIN`) and sign in with the superuser you created.

Create medicines (Oki Task, Synflex, …) then log episodes.

#### Deployment modes

The app ships with three compose files, one per deployment mode. Pick the one that matches where you run it and select it with `COMPOSE_FILE`.

| Mode | Compose file | HTTPS | Default port |
| --- | --- | --- | --- |
| Development | `docker-compose.local.yml` | no | `80` |
| LAN (local network) | `docker-compose.lan.yml` | no | `8383` |
| Public (domain) | `docker-compose.yml` | auto | `80`/`443` |

```bash
just up                                    # development (default)
COMPOSE_FILE=docker-compose.yml just up    # public, set DOMAIN to a real hostname
COMPOSE_FILE=docker-compose.lan.yml just up  # LAN, plain HTTP, never binds 443
```

For a LAN server at `192.168.1.10` on port `8383`, set in `.env`:

```env
DOMAIN=192.168.1.10
DJANGO_CSRF_TRUSTED_ORIGINS=http://192.168.1.10:8383
CADDY_PORT_HTTP=8383
```

When installing on a remote LAN/public box with `curl`, also fetch the LAN file and its Caddyfile:

```bash
curl -O https://raw.githubusercontent.com/lucaangioloni/headache_tracker/main/docker-compose.lan.yml
curl -O https://raw.githubusercontent.com/lucaangioloni/headache_tracker/main/Caddyfile.lan
```

### Option B — From source (development)

Clone the repository and build images locally. Use this to contribute, customize, or develop.

```bash
git clone https://github.com/lucaangioloni/headache_tracker.git
cd headache_tracker
cp .env.example .env
```

Edit `.env` to set a strong `DJANGO_SECRET_KEY` and your `DOMAIN`.

Then run the same setup steps:

```bash
just pull   # optional; skips the caddy pull warning
just up_build    # or: just ub / just ubd (detached)
just migrate
just createsuperuser
```

Open <http://localhost> and sign in. The frontend dev server hot-reloads on `localhost:5173`.

Override the published dev HTTP port with `CADDY_PORT_HTTP` in `.env` if needed.

## Commands

Default compose file is `docker-compose.local.yml`.

- `just up` / `just ub` / `just ubd` / `just upd` / `just du` / `just down` / `just logs`
- `just migrate` / `just makemigrations`
- `just test`
- `just createsuperuser`
- `just collectstatic`

Production pulls prebuilt images from GHCR (`backend` and `frontend`, tagged `latest` and the app version). Pin a version with `DJANGO_IMAGE` / `CADDY_IMAGE` in `.env`.

```bash
COMPOSE_FILE=docker-compose.yml just pull
COMPOSE_FILE=docker-compose.yml just up
```

Persistent state lives in `data/` (postgres, static, media, caddy, local `node_modules`). Back up or swap that folder.

Backend deps: edit `backend/requirements/*.in`, then `just requirements` (`uv pip compile`).

## Why was this developed?

I have been suffering of chronical migraines and severe headaches for two decades. Anyone who lives with chronic headaches knows how frustrating it is to accurately monitor triggers, track multiple medications and exact dosages, and spot long-term patterns using generic health apps or loose paper notes.

When preparing for consultations at headache clinics and neurologist visits, having clear, structured data is crucial:

- **Medication efficacy & timing**: Understanding which rescue medications (or combinations) actually work and how quickly they take effect.
- **Medication overuse prevention**: Accurately counting monthly intake days to avoid rebound headaches.
- **Trigger identification & metadata**: Recording context like sleep, stress, weather, and physical exertion alongside episode intensity.
- **Actionable reporting**: Generating clean monthly/yearly stats, frequency charts, and calendars ready to share directly with specialists.

This project was built to provide a fast, self-hostable, multi-user tracking platform with zero bloat—focused purely on actionable insights, complete privacy, and making daily condition management seamless.

## How was it developed?

I developed this in my free time over a single evening using AVA and AVACode from [Aidia](https://aidia.it/prodotti/ava/) and my supervision.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT
