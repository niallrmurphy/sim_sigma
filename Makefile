.PHONY: deps run help

PIP ?= pip3
PYTHON ?= python3
PYTHON_VERSION ?= python3.8

deps: ## Install system dependencies
	sudo apt install pkg-config libcairo2-dev $(PYTHON_VERSION)-tk

reqs: ## Install python requirements
	$(PIP) install -r requirements.txt

run: ## Run the simulation
	$(PYTHON) sim.py

help: ## This help function
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

