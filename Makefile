
#######################################################
# Project setup & housekeeeping 					  #
#######################################################

.PHONY: help
help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clean up Python compiled directories and caches
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

build: ## Build the project using poetry
	@echo "Building the project"
	@poetry build

requirements.txt: ## Generate requirements.txt from poetry dependencies
	@echo "Creating requirements.txt"
	@poetry export --output requirements.txt

check-next-version: ## Check next version with semantic-release
	@echo "Checking next version with semantic-release"
	@poetry run semantic-release -vv --noop version --print


#######################################################
# Linting & Formatting 							      #
#######################################################

lint: ## Run ruff linter and sort imports
	@echo "Running ruff linter and sorting imports"
	@poetry run ruff check --select I --fix .
	@poetry run ruff check .

format: ## Run ruff formatter
	@echo "Running ruff formatter"
	@poetry run ruff format .

check-types: ## Run mypy type checker
	@echo "Type checking with mypy"
	@poetry run mypy .

pre-commit-setup: ## Install pre-commit hooks for git
	@echo "Setting up pre-commit"
	@poetry run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

pre-commit: ## Run all pre-commit hooks
	@echo "Running pre-commit"
	@poetry run pre-commit run --all-files --color always && \
		poetry run pre-commit run --hook-stage pre-push --all-files --color always && \
		poetry run pre-commit run --hook-stage push --all-files --color always

#######################################################
# Testing 										      #
#######################################################


test: ## Run all tests with coverage report
	@echo "Running tests"
	@poetry run pytest -vv -s --cov=supabase_pydantic --cov-report=term-missing

coverage: ## Generate detailed HTML coverage report
	@echo "Running tests with coverage"
	@poetry run pytest --cov=supabase_pydantic --cov-report=term-missing --cov-report=html --cov-config=pyproject.toml

smoke-test: ## Run a quick test generating FastAPI models
	@echo "Running smoke test"
	@sb-pydantic gen --type pydantic --framework fastapi --local


#######################################################
# Documentation 									  #
#######################################################

serve-docs: ## Start local documentation server
	@echo "Building documentation"
	@poetry run mkdocs serve