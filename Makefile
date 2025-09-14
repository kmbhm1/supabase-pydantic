#######################################################
# Project setup & housekeeeping 					  #
#######################################################

.PHONY: help
help: ## Display this help message
	@echo "Available commands:"
	@echo ""
	@echo "Project Setup & Housekeeping:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*setup.*|^[a-zA-Z_-]+:.*?## .*clean.*' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Testing & Quality:"
	@grep -E '^test|^coverage|^tox|^lint|^typecheck|^smoke-test:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Building & Documentation:"
	@grep -E '^build|^requirements|^check-next-version|^serve-docs:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'

clean: ## Clean up Python compiled directories and caches
	@echo "Cleaning up Python compiled directories"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -f {} +
	@find . -type f -name "*.pyo" -exec rm -f {} +
	@find . -type d -name ".tox" -exec rm -rf {} +
	@poetry run pre-commit clean


#######################################################
# Build  & CICD										  #
#######################################################

build: ## Build the project using poetry
	@echo "Building the project"
	@poetry build

requirements.txt: ## Generate requirements.txt from poetry dependencies
	@echo "Creating requirements.txt"
	@rm -f requirements.txt
	@poetry export --without-hashes --output requirements.txt

check-next-version: ## Check next version with semantic-release
	@echo "Checking next version with semantic-release"
	@poetry run semantic-release -vv --noop version --print

#######################################################
# Linting & Formatting 							      #
#######################################################

lint: ## Run ruff linter and sort imports
	@echo "Running ruff linter and sorting imports"
	@poetry run ruff check --select I,UP007,F401,UP006 --fix .
	@poetry run ruff check .

format: ## Run ruff formatter
	@echo "Running ruff formatter"
	@poetry run ruff format .

typecheck: ## Run mypy type checker
	@echo "Type checking with mypy"
	@poetry run mypy .

vulture: ## Find unused code with vulture
	@echo "Finding unused code with vulture"
	@poetry run vulture src/ whitelist.py

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
	@poetry run pytest -vv -s --cov=src/supabase_pydantic --cov-report=term-missing --cov-fail-under=90

test-unit: ## Run only unit tests
	@echo "Running unit tests"
	@poetry run pytest -vv -s -m "unit" tests/unit/

test-integration: ## Run only integration tests with database connection
	@echo "Running integration tests with database connection"
	@RUN_DB_TESTS=1 poetry run pytest -vv -s -m "integration" tests/integration/

coverage: ## Generate detailed HTML coverage report
	@echo "Running tests with coverage"
	@poetry run pytest --cov=src/supabase_pydantic --cov-report=term-missing --cov-report=html --cov-config=pyproject.toml

tox: clean ## Run tests across multiple Python versions using tox
	@echo "Running tox for multiple Python versions"
	@poetry run tox

tox-py310: clean ## Run tests for Python 3.10 only
	@echo "Running tox for Python 3.10"
	@poetry run tox -e py310

tox-py311: clean ## Run tests for Python 3.11 only
	@echo "Running tox for Python 3.11"
	@poetry run tox -e py311

tox-py312: clean ## Run tests for Python 3.12 only
	@echo "Running tox for Python 3.12"
	@poetry run tox -e py312

tox-py313: clean ## Run tests for Python 3.13 only
	@echo "Running tox for Python 3.13"
	@poetry run tox -e py313

tox-py314: clean ## Run tests for Python 3.14 only
	@echo "Running tox for Python 3.14"
	@poetry run tox -e py314

tox-lint: clean ## Run linting with tox
	@echo "Running linting with tox"
	@poetry run tox -e lint

tox-mypy: clean ## Run type checking with tox
	@echo "Running type checking with tox"
	@poetry run tox -e mypy

smoke-test: ## Run a quick test generating FastAPI models
	@echo "Running smoke test"
	@sb-pydantic gen --type pydantic --framework fastapi --local

smoke-test-debug: ## Run a quick test with debugging generating FastAPI models
	@echo "Running smoke test"
	@sb-pydantic gen --type pydantic --framework fastapi --local --debug

smoke-test-sqlalchemy: ## Run a quick test generating SQLAlchemy models
	@echo "Running smoke test for SQLAlchemy"
	@sb-pydantic gen --type sqlalchemy --framework fastapi --local

smoke-test-sqlalchemy-debug: ## Run a quick test with debugging generating SQLAlchemy models
	@echo "Running smoke test for SQLAlchemy with debugging"
	@sb-pydantic gen --type sqlalchemy --framework fastapi --local --debug

smoke-test-mysql: ## Run a quick test generating FastAPI models from MySQL
	@echo "Running smoke test for MySQL"
	@sb-pydantic gen --type pydantic --framework fastapi --db-url=mysql://test_user:test_password@localhost:3306/test_db --db-type mysql

smoke-test-mysql-debug: ## Run a quick test with debugging generating FastAPI models from MySQL
	@echo "Running smoke test for MySQL with debugging"
	@sb-pydantic gen --type pydantic --framework fastapi --db-url=mysql://test_user:test_password@localhost:3306/test_db --db-type mysql --debug


#######################################################
# Documentation 									  #
#######################################################

serve-docs: ## Start local documentation server
	@echo "Building documentation"
	@poetry run mkdocs serve