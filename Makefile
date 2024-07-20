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

check-types:
	@echo "Type checking with mypy"
	@poetry run mypy .

pre-commit-setup:
	@echo "Setting up pre-commit"
	@poetry run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

pre-commit:
	@echo "Running pre-commit"
	@poetry run pre-commit run --all-files --color always && \
		poetry run pre-commit run --hook-stage pre-push --all-files --color always && \
		poetry run pre-commit run --hook-stage push --all-files --color always

sort-imports:
	@echo "Sorting imports"
	@poetry run isort .