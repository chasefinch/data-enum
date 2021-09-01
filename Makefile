default: lint test

format:
	isort .

lint:
	isort --check-only .
	flake8 .

test:
	coverage erase
	coverage run --source=data_enum -m pytest
	coverage report -m

develop:
	pip install -r requirements/develop.txt

.PHONY: default format lint test develop
