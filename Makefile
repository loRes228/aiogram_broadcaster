PACKAGE_DIRECTORY = aiogram_broadcaster
TESTS_DIRECTORY = tests
EXAMPLES_DIRECTORY = examples
BUTCHER_DIRECTORY = butcher
CACHE_DIRECTORY = .cache
CODE_DIRECTORIES = ${PACKAGE_DIRECTORY} ${TESTS_DIRECTORY} ${EXAMPLES_DIRECTORY} ${BUTCHER_DIRECTORY}


all: lint


# =====================================
# Environment
# =====================================

.PHONY: clean
clean:
	rm --force --recursive "${CACHE_DIRECTORY}"
	rm --force --recursive `find . -type d -name __pycache__`


# =====================================
# Code quality
# =====================================

.PHONY: lint
lint:
	mypy ${PACKAGE_DIRECTORY}
	ruff check ${PACKAGE_DIRECTORY}
	ruff format --check ${CODE_DIRECTORIES}

.PHONY: format
format:
	ruff format ${CODE_DIRECTORIES}
	ruff check --fix --unsafe-fixes ${PACKAGE_DIRECTORY}


# =====================================
# Testing
# =====================================

.PHONY: test
test:
	pytest


# =====================================
# Project
# =====================================

.PHONY: butcher
butcher:
	python -m butcher
	$(MAKE) format

.PHONY: release
release:
	git tag "v$(shell hatch version)"
