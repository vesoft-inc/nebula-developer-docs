PYTHON ?= .venv/bin/python
PORT ?= 8001
VERSION ?= preview

.PHONY: help setup serve serve-all serve-zh serve-en build build-zh build-en check release

help:
	@echo "make setup       Install the documentation tools"
	@echo "make serve       Preview Chinese and English (default: preview)"
	@echo "make serve-all   Preview all languages and versions"
	@echo "make serve-zh    Preview Chinese only"
	@echo "make serve-en    Preview English only"
	@echo "make build-zh    Rebuild one Chinese version"
	@echo "make build-en    Rebuild one English version"
	@echo "make check       Build and check everything"
	@echo "make release     Generate the two official-site artifacts"
	@echo "Options: PORT=8001 VERSION=preview"

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements-preview.txt

serve:
	$(PYTHON) scripts/docs.py serve --port $(PORT) --version $(VERSION)

serve-all:
	$(PYTHON) scripts/docs.py serve --port $(PORT) --version all

serve-zh:
	$(PYTHON) scripts/docs.py serve --port $(PORT) --lang zh --version $(VERSION)

serve-en:
	$(PYTHON) scripts/docs.py serve --port $(PORT) --lang en --version $(VERSION)

build-zh:
	$(PYTHON) scripts/docs.py build --port $(PORT) --lang zh --version $(VERSION)
	$(PYTHON) scripts/check_site.py --lang zh --version $(VERSION)

build-en:
	$(PYTHON) scripts/docs.py build --port $(PORT) --lang en --version $(VERSION)
	$(PYTHON) scripts/check_site.py --lang en --version $(VERSION)

build:
	$(PYTHON) scripts/docs.py build --port $(PORT)

check: build
	$(PYTHON) scripts/check_site.py

release:
	$(PYTHON) scripts/docs.py build --production
	$(PYTHON) scripts/check_site.py --production
