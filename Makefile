install:
	poetry install

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --force-reinstall dist/*.whl

lint:
	poetry run flake8 page_analyzer

selfcheck:
	poetry check

check: selfcheck lint

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
.PHONY: install

all: db-reset schema-load start

schema-load:
	psql railway < database.sql

generate:
	node ./bin/load.js

db-reset:
	dropdb railway || true
	createdb railway

db-create:
	createdb analyzer || echo 'skip'

connect:
	psql -d analyzer