PACKAGE_DIRECTORY = aiogram_broadcaster
EXAMPLES_DIRECTORY = examples
TESTS_DIRECTORY = tests


all: lint


# =====================================
# Environment
# =====================================

.PHONY: clean
clean:
	rm --force --recursive {.cache.,.coverage,reports}
	rm --force --recursive `find . -type d -name __pycache__`


# =====================================
# Code quality
# =====================================

CODE_DIRECTORIES = ${PACKAGE_DIRECTORY} ${EXAMPLES_DIRECTORY}

.PHONY: lint
lint:
	mypy ${CODE_DIRECTORIES}
	ruff check ${CODE_DIRECTORIES}
	ruff format --check ${CODE_DIRECTORIES}

.PHONY: format
format:
	ruff format ${CODE_DIRECTORIES}
	ruff check --fix ${CODE_DIRECTORIES}


# =====================================
# Testing
# =====================================

REPORTS_DIRECTORY = reports

.PHONY: test
test:
	pytest

.PHONY: test-report
test-report:
	pytest --cov ${PACKAGE_DIRECTORY} --html "${REPORTS_DIRECTORY}/tests/index.html"
	coverage html --directory "${REPORTS_DIRECTORY}/coverage"

.PHONY: test-report-view
test-report-view: test-report
	python -m webbrowser "${CURDIR}/${REPORTS_DIRECTORY}/tests/index.html"
	python -m webbrowser "${CURDIR}/${REPORTS_DIRECTORY}/coverage/index.html"
