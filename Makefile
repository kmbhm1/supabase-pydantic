
#######################################################
# Project setup & housekeeeping 					  #
#######################################################

clean:
	@echo "Cleaning up Python compiled directories"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -f {} +
	@find . -type f -name "*.pyo" -exec rm -f {} +
	@poetry run pre-commit clean


#######################################################
# Build  & CICD										  #
#######################################################

build:
	@echo "Building the project"
	@poetry build

requirements.txt:
	@echo "Creating requirements.txt"
	@poetry export --output requirements.txt

check-next-version:
	@echo "Checking next version with semantic-release"
	@poetry run semantic-release -vv --noop version --print


#######################################################
# Linting & Formatting 							      #
#######################################################

sort-imports:
	@echo "Sorting imports"
	@poetry run isort .

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

#######################################################
# Testing 										      #
#######################################################


test:
	@echo "Running tests"
	@poetry run pytest -vv -s --cov=supabase_pydantic --cov-report=term-missing

coverage:
	@echo "Running tests with coverage"
	@poetry run pytest --cov=supabase_pydantic --cov-report=term-missing --cov-report=html --cov-config=pyproject.toml