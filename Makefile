CODE_DIRS = aiogram_broadcaster examples


.PHONY: lint
lint:
	mypy ${CODE_DIRS}
	ruff check ${CODE_DIRS}
	ruff format --check ${CODE_DIRS}


.PHONY: format
format:
	ruff format ${CODE_DIRS}
	ruff check --fix ${CODE_DIRS}


.PHONY: release
release:
	git add .
	git commit -m "Release $(shell hatch version)"
	git tag v$(shell hatch version)
