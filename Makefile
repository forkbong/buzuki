# Simple Makefile to automate common tasks

init:
	poetry install
	./scripts/elastic.sh install
	./scripts/elastic.sh start
	./manage.py index

run:
	-./scripts/elastic.sh start
	FLASK_APP=buzuki FLASK_ENV=development flask run

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

.PHONY: init run test coverage report
