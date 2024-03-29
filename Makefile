CODE_DIRS = aiogram_broadcaster examples


.PHONY: lint
lint:
	mypy ${CODE_DIRS}
	ruff check ${CODE_DIRS}
	ruff format --check ${CODE_DIRS}


.PHONY: format
format:
	ruff check --fix ${CODE_DIRS}
	ruff format ${CODE_DIRS}
