#!/bin/bash

# Check for wait-for-it.sh script
if [ ! -f "./wait-for-it.sh" ]; then
  echo "wait-for-it.sh script not found. Downloading..."
  curl -O https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
  chmod +x wait-for-it.sh
fi

# List of scenarios
# scenarios=("scenario1" "scenario2" "scenario3")
scenarios=("sb-countries")

# Define the path to docker-compose.yml
DOCKER_COMPOSE_PATH="./docker-compose.yml"

# Loop through each scenario
for scenario in "${scenarios[@]}"; do
  echo "Running $scenario..."

  # Set environment variable for the scenario number
  export SCENARIO=${scenario}

  # Tear down any existing database structure
  echo "Running teardown..."
  docker compose -f "$DOCKER_COMPOSE_PATH" run --rm teardown

  # Initialize the database with the new scenario
  echo "Running init..."
  docker compose -f "$DOCKER_COMPOSE_PATH" run --rm init

  # Run the test command to generate Python files
  echo "Running test-runner..."
  docker compose -f "$DOCKER_COMPOSE_PATH" run --rm test-runner

  # Tear down the database structure at the end
  echo "Running teardown..."
  docker compose -f "$DOCKER_COMPOSE_PATH" run --rm teardown

  echo "$scenario completed."
done
