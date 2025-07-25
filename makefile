migrate:
	DB_HOST=$(host) alembic revision --autogenerate -m "$(m)"

migrate-local:
	HOST=localhost alembic revision --autogenerate -m "$(m)"

migrate-docker:
	HOST=postgres alembic revision --autogenerate -m "$(m)"