#!/usr/bin/env make
.PHONY: help install test serve docs verify list

PYTHON ?= python3
export ACADEMY_CURRICULUM := $(CURDIR)/curriculum
export ACADEMY_DOCS := $(CURDIR)/docs
export ACADEMY_DATA := $(CURDIR)/.academy-data
export PYTHONPATH := $(CURDIR)/platform

help:
	@echo "Pi SDR Academy"
	@echo "  make install   editable install of the academy package"
	@echo "  make test      platform unit tests"
	@echo "  make serve     dojo UI on 127.0.0.1:8080"
	@echo "  make docs      offline docs on 127.0.0.1:8000"
	@echo "  make list      print modules"
	@echo "  make verify    check local tooling (best on a Pi image)"

install:
	$(PYTHON) -m pip install -e ./platform

test:
	$(PYTHON) -m pytest platform/tests -q

serve:
	$(PYTHON) -m academy serve --host 127.0.0.1 --port 8080

docs:
	$(PYTHON) -m academy docs --host 127.0.0.1 --port 8000

list:
	$(PYTHON) -m academy list

verify:
	bash scripts/verify_environment.sh
