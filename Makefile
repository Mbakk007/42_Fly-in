.PHONY: install run debug lint lint-strict clean

MAP ?= map.txt

install:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

run:
	python3 main.py $(MAP)

debug:
	python3 -m pdb main.py $(MAP)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache venv