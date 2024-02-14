SHELL = /bin/bash
PYTHON ?= python

init:
	sh scripts/init.sh

install_dev:
	$(PYTHON) -m pip install -r requirements-dev.txt -e .
	$(PYTHON) -m playwright install chromium
	$(PYTHON) -m pre_commit install

compile:
	$(PYTHON) -m piptools compile --resolver=backtracking --no-emit-index-url -o requirements.txt pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --no-emit-index-url --extra=dev -o requirements-dev.txt pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --no-emit-index-url --extra=docs -o requirements-docs.txt pyproject.toml

sync:
	$(PYTHON) -m piptools sync requirements-dev.txt
	$(PYTHON) -m pip install -e .

up: compile sync

docs:
	cd docs/ && $(PYTHON) -m quartodoc build && quarto render && cd ..

.PHONY: install_dev compile sync up docs
