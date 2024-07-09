build:
	@echo "Building the project"
	@poetry build

requirements.txt:
	@echo "Creating requirements.txt"
	@poetry export --output requirements.txt

noop-next:
	@echo "Checking next version with semantic-release ..."
	@poetry run semantic-release -vv --noop version --print