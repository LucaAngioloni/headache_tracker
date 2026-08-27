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
