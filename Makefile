build:
	docker compose build

lint:
	docker compose run --rm -it main /app/lint.sh

shell:
	docker compose run --rm -it main bash

test:
	docker compose run --rm main pytest -o cache_dir=/app/.pytest-cache -svvv --pdb --doctest-modules youtool.py tests.py

.PHONY: build lint shell test
