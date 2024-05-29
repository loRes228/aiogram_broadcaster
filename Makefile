PACKAGE_DIRECTORY = aiogram_broadcaster
EXAMPLES_DIRECTORY = examples
TESTS_DIRECTORY = tests
CODE_DIRECTORIES = ${PACKAGE_DIRECTORY} ${TESTS_DIRECTORY} ${EXAMPLES_DIRECTORY}
CACHE_DIRECTORY = .cache
REPORTS_DIRECTORY = ${CACHE_DIRECTORY}/reports


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
	ruff check --fix ${PACKAGE_DIRECTORY}


# =====================================
# Testing
# =====================================

.PHONY: test
test:
	pytest

.PHONY: test-report
test-report:
	pytest --cov ${PACKAGE_DIRECTORY} --html "${REPORTS_DIRECTORY}/tests/index.html"
	coverage html --directory "${REPORTS_DIRECTORY}/coverage"

.PHONY: test-report-view
test-report-view:
	-$(MAKE) test-report
	python -m webbrowser "${CURDIR}/${REPORTS_DIRECTORY}/tests/index.html"
	python -m webbrowser "${CURDIR}/${REPORTS_DIRECTORY}/coverage/index.html"
