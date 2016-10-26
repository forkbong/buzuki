# Simple Makefile to automate common tasks

init:
	poetry install

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
