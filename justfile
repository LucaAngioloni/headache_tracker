compose_file := env_var_or_default("COMPOSE_FILE", "docker-compose.local.yml")
export COMPOSE_FILE := compose_file

alias stop := down
alias ub := up_build
alias ds := django_shell
alias upd := up_detached
alias du := down_up
alias l := logs
alias ubd := up_build_detached

default:
  @just --list

build *args='':
  @echo "Building docker images..."
  @docker compose build {{args}}

up *args='':
  @echo "Starting up docker containers..."
  @docker compose up --remove-orphans {{args}}

up_build *args='':
  @echo "Building and starting up docker containers..."
  @docker compose up --build --remove-orphans {{args}}

up_detached *args='':
  @echo "Starting up docker containers in detach mode..."
  @docker compose up -d --remove-orphans {{args}}

up_build_detached *args='':
  @echo "Building and starting up docker containers in detach mode..."
  @docker compose up -d --build --remove-orphans {{args}}

restart *args='':
  @echo "Restart docker containers..."
  @docker compose restart {{args}}

down_up *args='':
  @echo "Rebuilding and restarting docker containers..."
  @docker compose down
  @docker compose up --build --remove-orphans {{args}}

down *args='':
  @echo "Stopping docker containers..."
  @docker compose down {{args}}

pull *args='':
  @echo "Pulling latest docker images..."
  @docker compose pull {{args}}

prune *args='':
  @echo "Killing docker containers and removing volumes..."
  @docker compose down -v {{args}}

logs *args:
  @docker compose logs -f {{args}}

migrate *args='':
  @echo "Running database migrations..."
  @docker compose run --rm django python manage.py migrate {{args}}

makemigrations *args='':
  @echo "Creating new database migrations..."
  @docker compose run --rm django python manage.py makemigrations {{args}}

django_shell:
  @echo "Opening Django shell..."
  @docker compose run --rm django python manage.py shell

createsuperuser:
  @echo "Creating Django superuser..."
  @docker compose run --rm django python manage.py createsuperuser

collectstatic:
  @echo "Collecting static files..."
  @docker compose run --rm django python manage.py collectstatic --noinput

requirements:
  @./backend/requirements/upgrade.sh

bump_version version:
  @echo "Bumping app version to {{version}}..."
  @python3 backend/bump_version.py {{version}}

run *args:
  @echo "Running command in django container..."
  @docker compose run --rm django python manage.py {{args}}

test *args='':
  @echo "Running tests in django container..."
  @docker compose run --rm django pytest {{args}}

makemessages:
  @echo "Making message files for translations..."
  @docker compose run --rm django python manage.py makemessages -a

compilemessages *args='':
  @echo "Compiling message files for translations..."
  @docker compose run --rm django python manage.py compilemessages {{args}}

db_export file="backups/headache_tracker.sql":
  #!/usr/bin/env bash
  set -euo pipefail
  mkdir -p "$(dirname "{{file}}")"
  echo "Exporting database to {{file}}..."
  docker compose up -d db
  docker compose exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done' >/dev/null
  docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl --clean --if-exists' > "{{file}}"
  echo "Exported {{file}}"

db_import file:
  #!/usr/bin/env bash
  set -euo pipefail
  if [ ! -f "{{file}}" ]; then
    echo "SQL dump not found: {{file}}" >&2
    exit 1
  fi
  echo "Importing {{file}} (replaces existing database objects)..."
  docker compose up -d db
  docker compose exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done' >/dev/null
  docker compose stop django
  docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' < "{{file}}"
  docker compose start django
  echo "Imported {{file}}"
