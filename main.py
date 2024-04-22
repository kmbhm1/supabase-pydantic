# Example usage to generate Pydantic models and save them
import os
from util import (
    construct_table_info,
    create_connection,
    fetch_foreign_key_details,
    fetch_table_column_details,
    generate_imports_for_pydantic_models,
    generate_pydantic_model,
    generate_pydantic_parent_name,
)
import pprint
from dotenv import load_dotenv, find_dotenv

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Replace these variables with your database connection details
db_name = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")


def check_connection(conn):
    if conn.closed:
        print("Connection is closed.")
        return False
    else:
        print("Connection is open.")
        return True


def check_readiness():
    """
    Check if environment variables are set correctly.
    """
    check = {
        "DB_NAME": db_name,
        "DB_USER": user,
        "DB_PASS": password,
        "DB_HOST": host,
        "DB_PORT": port,
    }
    for k, v in check.items():
        # print(k, v)
        if v is None:
            print(
                f"Environment variables not set correctly. {k} is missing. Please set it in .env file."
            )
            print("Exiting...")
            return False

    return True


# Main function to execute the whole process
def main():
    # Load environment variables from .env file & check if they are set correctly
    load_dotenv(find_dotenv())
    assert check_readiness()

    default_directory = "supabase_types"
    default_parent_filename = "supabase_pydantic_parent_models.py"

    try:
        # Create a connection to the database & check if connection is successful
        conn = create_connection(db_name, user, password, host, port)
        assert check_connection(conn)

        # Fetch table column details & foreign key details
        column_details = fetch_table_column_details(conn)
        fk_details = fetch_foreign_key_details(conn)
        tables = construct_table_info(column_details, fk_details)
        for t in tables:
            print(t)

    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

    # Create Pydantic models file
    parent_models_string = generate_imports_for_pydantic_models(tables) + "\n\n"
    parent_models_string += "".join(
        [
            generate_pydantic_model(table, generate_pydantic_parent_name) + "\n\n"
            for table in tables
        ]
    )

    # Check if the directory exists, if not, create it
    if not os.path.exists(default_directory):
        os.makedirs(default_directory)

    # Define the full path to the file
    file_path = os.path.join(default_directory, default_parent_filename)

    # Write the imports and model string to the file, overwriting if it exists
    with open(file_path, "w") as file:
        file.write(parent_models_string)


if __name__ == "__main__":
    main()
