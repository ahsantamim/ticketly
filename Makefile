# Shortcuts for the Docker Compose stack. See README.md.
.PHONY: up down logs migrate test shell

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f web

# Do not run until the custom User model (TIC-7) exists.
migrate:
	docker compose run --rm web python manage.py migrate

test:
	docker compose run --rm --build test

shell:
	docker compose run --rm web python manage.py shell
