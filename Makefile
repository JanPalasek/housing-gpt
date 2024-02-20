SHELL = /bin/bash
PYTHON ?= python

init:
	sh scripts/init.sh

install_dev:
	$(PYTHON) -m pip install -r requirements.txt -e .
	$(PYTHON) -m playwright install chromium
	$(PYTHON) -m pre_commit install

compile:
	$(PYTHON) -m piptools compile --resolver=backtracking --no-emit-index-url --extra=dev -o requirements.txt pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --no-emit-index-url --extra=docs -o requirements-docs.txt pyproject.toml

sync:
	$(PYTHON) -m piptools sync requirements.txt
	$(PYTHON) -m pip install -e .

up: compile sync

docs:
	cd docs/ && $(PYTHON) -m quartodoc build && quarto render && cd ..

deploy_dashboard:
	@echo "Deploying..."
	quarto render dashboard.qmd
	rsconnect deploy shiny . --name janpalasek --title housing-gpt
	rm app.py

.PHONY: install_dev compile sync up docs deploy_dashboard
