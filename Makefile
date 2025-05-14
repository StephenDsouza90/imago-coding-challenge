# Variables
PYTHON = python3.12

# Preparation
.PHONY: venv

lint:
	./venv/bin/ruff check --fix

format:
	./venv/bin/ruff format