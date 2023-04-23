coverage:
	poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run mypy .
	poetry run black . --check
	poetry run isort . --check
	poetry run flake8 .

unit_tests:
	cd ghost && poetry run python -m pytest tests/unit_tests

integration_tests:
	cd ghost && poetry run python -m pytest tests/integration_tests -s
