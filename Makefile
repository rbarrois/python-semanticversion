PACKAGE=semantic_version
TESTS_DIR=tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)
FLAKE8 = flake8

all: default


default:

.PHONY: all default


# Package management
# ==================


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/


update:
	pip install --upgrade pip setuptools
	pip install --upgrade -r requirements_dev.txt
	pip freeze


release:
	fullrelease

.PHONY: clean update release

# Tests and quality
# =================


# DOC: Run tests for all supported versions (creates a set of virtualenvs)
testall:
	tox


# DOC: Run tests for the currently installed version
test:
	python -Wdefault setup.py test

# DOC: Perform code quality tasks
lint: check-manifest flake8

# DOC: Verify that MANIFEST.in and .gitignore are consistent
check-manifest:
	check-manifest

# Note: we run the linter in two runs, because our __init__.py files has specific warnings we want to exclude
# DOC: Verify code quality
flake8:
	$(FLAKE8) --config .flake8 --exclude $(PACKAGE)/__init__.py $(PACKAGE) $(TESTS_DIR) setup.py
	$(FLAKE8) --config .flake8 --ignore F401 $(PACKAGE)/__init__.py

# DOC: Run tests with coverage collection
coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

.PHONY: testall test lint check-manifest flake8 coverage


# Documentation
# =============


# DOC: Compile the documentation
doc:
	$(MAKE) -C $(DOC_DIR) html


# DOC: Show this help message
help:
	@grep -A1 '^# DOC:' Makefile \
	 | awk '    					\
	    BEGIN { FS="\n"; RS="--\n"; opt_len=0; }    \
	    {    					\
		doc=$$1; name=$$2;    			\
		sub("# DOC: ", "", doc);    		\
		sub(":", "", name);    			\
		if (length(name) > opt_len) {    	\
		    opt_len = length(name)    		\
		}    					\
		opts[NR] = name;    			\
		docs[name] = doc;    			\
	    }    					\
	    END {    					\
		pat="%-" (opt_len + 4) "s %s\n";    	\
		asort(opts);    			\
		for (i in opts) {    			\
		    opt=opts[i];    			\
		    printf pat, opt, docs[opt]    	\
		}    					\
	    }'

.PHONY: doc help
