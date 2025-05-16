# Variables
PYTHON = python3.12

# Preparation
.PHONY: venv

lint:
	./venv/bin/ruff check --fix

format:
	./venv/bin/ruff format

unit-test:
	./venv/bin/pytest src/tests/unit

e2e-test:
	./venv/bin/pytest src/tests/e2e