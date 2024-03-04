import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace these variables with your database connection details
db_name = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name, user=user, password=password, host=host, port=port
)

# Create a cursor object
cur = conn.cursor()

# SQL query to fetch table schema details
query = """
SELECT table_schema
    , table_name
    , column_name
    , data_type
    , character_maximum_length
FROM information_schema.columns
WHERE 
    table_schema = 'public'
ORDER BY table_schema, table_name, ordinal_position;
"""

# Execute the query
cur.execute(query)

# Fetch all the results
results = cur.fetchall()

# Print the schema details
for row in results:
    print(
        f"Schema: {row[0]}, Table: {row[1]}, Column: {row[2]}, Data Type: {row[3]}, Max Length: {row[4]}"
    )

# Close the cursor and connection
cur.close()
conn.close()
