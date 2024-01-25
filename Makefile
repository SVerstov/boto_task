.PHONY: init migrate migrations downgrade run


init:
	poetry shell
	poetry install --no-root


migrate:
	poetry run alembic upgrade head


migrations:
	poetry run alembic revision --autogenerate --message "$(word 2,$(MAKECMDGOALS))"

downgrade:
	poetry run alembic downgrade -1

run:
	poetry run python main.py