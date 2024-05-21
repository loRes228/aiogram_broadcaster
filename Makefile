PACKAGE_DIRECTORY = aiogram_broadcaster
EXAMPLES_DIRECTORY = examples
CODE_DIRECTORIES = ${PACKAGE_DIRECTORY} ${EXAMPLES_DIRECTORY}


# =====================================
# Environment
# =====================================

.PHONY: clean
clean:
	rm --force --recursive {.cache}
	rm --force --recursive `find . -type d -name __pycache__`


# =====================================
# Code quality
# =====================================

.PHONY: lint
lint:
	mypy ${CODE_DIRECTORIES}
	ruff check ${CODE_DIRECTORIES}
	ruff format --check ${CODE_DIRECTORIES}


.PHONY: format
format:
	ruff format ${CODE_DIRECTORIES}
	ruff check --fix ${CODE_DIRECTORIES}
