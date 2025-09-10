.PHONY: pre-condition
pre-condition:
ifndef VIRTUAL_ENV
	@echo 'Python virtual environment not activated. Activate with `source .venv/bin/activate`.'
	@echo 'Exiting...'
	exit 1
endif

.PHONY: dev-install
dev-install: pre-condition
	python -m pip install -e .
	python -m pip install '.[dev]'

.PHONY: check-format
check-format: pre-condition
	ruff format --diff ./src ./tests

.PHONY: lint
lint: pre-condition
	ruff check ./src ./tests

.PHONY: test
test: pre-condition
	python -m pytest

.PHONY: build
build: pre-condition
	python -m build
	python -m twine check dist/*
