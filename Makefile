build:
	docker compose build

lint:
	docker compose run --rm -it main /app/lint.sh

shell:
	docker compose run --rm -it main bash

test:
	docker compose run --rm main pytest -o cache_dir=/app/.pytest-cache -svvv --pdb --doctest-modules youtool.py tests.py

test-release:
	docker compose run --rm main /app/release.sh --test

release:
	docker compose run --rm main /app/release.sh

.PHONY: build lint shell test test-release release
