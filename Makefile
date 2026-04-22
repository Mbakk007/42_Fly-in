.PHONY: install run debug lint lint-strict clean
PYTHON := venv/bin/python

MAP ?= maps/easy/01_linear_path.txt

install:
	python3 -m venv venv
	pip install flake8 mypy

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache venv