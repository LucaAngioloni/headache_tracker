# Headache Tracker

Personal multi-user headache diary: medicines, episodes with doses, triggers, calendar, stats.

## First run

```bash
cp .env.example .env
just ubd
just migrate
just createsuperuser
```

Open <http://localhost> and sign in.

Create medicines (Oki Task, Synflex, …) then log episodes. There is no notebook import.

## Commands

Default compose file is `docker-compose.local.yml`.

- `just up` / `just ub` / `just ubd` / `just upd` / `just du` / `just down` / `just logs`
- `just migrate` / `just makemigrations`
- `just test`
- `just createsuperuser`
- `just collectstatic`

Production: `COMPOSE_FILE=docker-compose.yml just build` then `COMPOSE_FILE=docker-compose.yml just up`.

Persistent state lives in `data/` (postgres, static, media, caddy, local `node_modules`). Back up or swap that folder.

Backend deps: edit `backend/requirements/*.in`, then `just requirements` (`uv pip compile`).
