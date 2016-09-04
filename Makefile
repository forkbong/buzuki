# Simple Makefile to automate common tasks

init:
	poetry install
	python3 manage.py db init
	python3 manage.py db migrate
	python3 manage.py db upgrade
	python3 manage.py import

test:
	isort --check-only .
	flake8 buzuki tests *.py
	python3 -m pytest -s tests

coverage:
	coverage run --branch --source buzuki -m pytest tests --strict
	coverage report --show-missing
	coverage html

report: coverage
	$(BROWSER) htmlcov/index.html

.PHONY: init test coverage report
