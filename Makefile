# Simple Makefile to automate common tasks

init:
	poetry install

run:
	nohup flock -n /tmp/buzuki-search.lock buzuki-search > /tmp/buzuki-search.log 2>&1 &
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

requirements.txt: poetry.lock
	poetry export --with dev --without-hashes -f requirements.txt > requirements.txt

.PHONY: init run test coverage report
