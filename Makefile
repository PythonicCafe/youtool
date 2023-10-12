build:
	docker compose build

lint:
	docker compose run --rm -it main /app/lint.sh

shell:
	docker compose run --rm -it main bash

test:
	docker compose exec main pytest

test-v:
	docker compose exec main pytest -vvv

.PHONY: build lint shell test test-v
