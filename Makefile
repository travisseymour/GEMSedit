# Makefile
# --------
# Usage:
# make [COMMAND]
# E.g.:
# make build

.PHONY: build clean test clean-pycache format

install:
	pip install -U pip wheel
	pip install .[dev]
	pip uninstall gemsedit -y
	make clean

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
