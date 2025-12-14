# Makefile
# --------
# Usage:
# make [COMMAND]
# E.g.:
# make build

.PHONY: build clean test clean-pycache format install

SHELL := /usr/bin/env bash

install:
	@if [[ -n "$$VIRTUAL_ENV" ]]; then \
	    echo "Installing GEMSedit dependencies into virtual environment $$VIRTUAL_ENV"; \
	    pip install -U pip wheel; \
	    pip install -e .[dev]; \
	else \
	    echo "Not in a virtual environment, install one first and then try again."; \
	fi

uninstall:
	@if [[ -n "$$VIRTUAL_ENV" ]]; then \
	    echo "Uninstalling GEMSedit dependencies from virtual environment $$VIRTUAL_ENV"; \
	    pip uninstall GEMS; \

	else \
	    echo "Not in a virtual environment, nothing to uninstall."; \
	fi

format:
	ruff check gemsedit --fix
	ruff format gemsedit
	black gemsedit

build:
	python -m build

clean:
	rm -rf build dist *.egg-info

test:
	PYTHONPATH=$(shell pwd) pytest tests/
	PYTHONPATH=$(shell pwd) pytest tests/unittests/
	PYTHONPATH=$(shell pwd) pytest tests/guitests/

clean-pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
