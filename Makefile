PACKAGE=semantic_version
TESTS_DIR=tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

# Dependencies
DJANGO_VERSION ?= 1.8
PYTHON_VERSION := $(shell python --version)
NEXT_DJANGO_VERSION=$(shell python -c "v='$(DJANGO_VERSION)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")


all: default


default:


install-deps: auto_dev_requirements_django$(DJANGO_VERSION).txt
	pip install --upgrade pip setuptools
	pip install --upgrade -r $<
	pip freeze

auto_dev_requirements_%.txt: dev_requirements_%.txt dev_requirements.txt requirements.txt
	grep --no-filename "^[^#-]" $^ | grep -v "^Django" > $@
	echo "Django>=$(DJANGO_VERSION),<$(NEXT_DJANGO_VERSION)" >> $@

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -f auto_dev_requirements_*
	@rm -rf tmp_test/


test: install-deps
	python -W default setup.py test

pylint:
	pylint --rcfile=.pylintrc --report=no $(PACKAGE)/

coverage: install-deps
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

coverage-xml-report: coverage
	$(COVERAGE) xml "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	$(MAKE) -C $(DOC_DIR) html


.PHONY: all default clean coverage doc install-deps pylint test
