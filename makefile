migrate:
	alembic upgrade head

makemigrations:
	DB_HOST=$(host) alembic revision --autogenerate -m "$(m)"


makemigrations-local:
	HOST=localhost alembic revision --autogenerate -m "$(m)"

makemigrations-docker:
	HOST=postgres alembic revision --autogenerate -m "$(m)"


