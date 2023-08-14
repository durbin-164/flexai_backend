server:
	uvicorn main:app --reload

server_dev:
	poetry shell

alembic_migration:
	alembic revision --autogenerate -m "$(m)"

alembic_upgrade:
	alembic upgrade head