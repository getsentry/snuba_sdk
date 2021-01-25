SHELL = /bin/bash

VENV_PATH = .venv

help:
	@echo "Thanks for your interest in the Snuba SnQL SDK!"
	@echo
	@echo "make lint: Run linters"
	@echo "make tests: Run tests"
	@echo "make format: Run code formatters (destructive)"
	@echo
	@echo "Also make sure to read ./CONTRIBUTING.md"
	@false

.venv:
	virtualenv -ppython3.9 $(VENV_PATH)
	$(VENV_PATH)/bin/pip install -r test-requirements.txt
	$(VENV_PATH)/bin/pip install -r linter-requirements.txt

setup-git:
	pip install 'pre-commit==2.9.3'
	pre-commit install --install-hooks

dist: .venv
	rm -rf dist build
	$(VENV_PATH)/bin/python setup.py sdist bdist_wheel

.PHONY: dist

format: .venv
	$(VENV_PATH)/bin/flake8 tests examples snuba_sdk
	$(VENV_PATH)/bin/black tests examples snuba_sdk
	$(VENV_PATH)/bin/mypy --config-file mypy.ini tests examples snuba_sdk

.PHONY: format

tests: .venv
	@$(VENV_PATH)/bin/pytest

.PHONY: tests

check: lint tests
.PHONY: check

lint: .venv
	$(VENV_PATH)/bin/flake8 tests examples snuba_sdk
	$(VENV_PATH)/bin/black --check tests examples snuba_sdk
	$(VENV_PATH)/bin/mypy --config-file mypy.ini tests examples snuba_sdk

.PHONY: lint
