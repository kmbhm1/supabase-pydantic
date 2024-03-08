# Example usage to generate Pydantic models and save them
import os
from util import (
    connect_to_database,
    generate_imports_string,
    generate_pydantic_parent_model,
    get_table_schema,
    remove_last_two_newlines,
    save_model_to_file,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace these variables with your database connection details
db_name = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")


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
        if v is None:
            print(
                f"Environment variables not set correctly. {k} is missing. Please set it in .env file."
            )
            print("Exiting...")
            return False


def main():
    """
    Main function to generate Pydantic models and save them to a file.
    """
    directory = "supabase-py-def"
    filename = "SupabaseParentBaseModels.py"

    conn = connect_to_database(db_name, user, password, host, port)
    if conn:
        schema_details = get_table_schema(conn)
        imports_str = generate_imports_string(schema_details)
        all_models_str = ""
        for table_name, columns in schema_details.items():
            model_str = generate_pydantic_parent_model(table_name, columns)
            all_models_str += model_str + "\n\n"
        all_models_str = remove_last_two_newlines(all_models_str)
        save_model_to_file(directory, filename, imports_str, all_models_str)
        print(f"Models saved to {os.path.join(directory, filename)}")
        conn.close()


if __name__ == "__main__":
    main()
