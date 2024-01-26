.PHONY: init migrate migrations downgrade run


install:
	poetry install --no-root

init:
	poetry shell



migrate:
	poetry run alembic upgrade head


migrations:
	poetry run alembic revision --autogenerate --message "$(word 2,$(MAKECMDGOALS))"

downgrade:
	poetry run alembic downgrade -1

run:
	poetry run python main.py

test:
	poetry run pytest --disable-warnings