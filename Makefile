build:
	@echo "Building the project"
	@poetry build

requirements.txt:
	@echo "Creating requirements.txt"
	@poetry export --output requirements.txt

noop-next:
	@echo "Checking next version with semantic-release"
	@poetry run semantic-release -vv --noop version --print

lint:
	@echo "Running ruff linter"
	@poetry run ruff check .

format:
	@echo "Running ruff formatter"
	@poetry run ruff format .

pre-commit:
	@echo "Running pre-commit"
	@poetry run pre-commit run --all-files

sort-imports:
	@echo "Sorting imports"
	@poetry run isort .