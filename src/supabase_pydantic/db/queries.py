"""SQL queries for database schema introspection.

This module contains SQL queries used for introspecting database schemas.
Currently focused on PostgreSQL, but designed to be extended for other databases.
"""

# PostgreSQL schema query to retrieve all non-system schemas
POSTGRES_SCHEMAS_QUERY = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
"""

# PostgreSQL query to get all tables and their columns in a schema
POSTGRES_TABLES_AND_COLUMNS_QUERY = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.column_default,
    c.is_nullable,
    c.data_type,
    c.character_maximum_length,
    t.table_type,
    c.identity_generation
FROM
    information_schema.columns AS c
JOIN
    information_schema.tables AS t ON c.table_name = t.table_name AND c.table_schema = t.table_schema
WHERE
    c.table_schema = %s
    AND (t.table_type = 'BASE TABLE' OR t.table_type = 'VIEW')
ORDER BY
    c.table_schema, c.table_name, c.ordinal_position;
"""

# PostgreSQL query to get foreign key relationships in a schema
POSTGRES_FOREIGN_KEYS_QUERY = """
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = %s;
"""

# PostgreSQL query to get constraints in a schema
POSTGRES_CONSTRAINTS_QUERY = """
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    array_agg(a.attname) AS columns,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM
    pg_constraint
JOIN
    pg_attribute AS a ON a.attnum = ANY (conkey) AND a.attrelid = conrelid
WHERE
    connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
GROUP BY
    conname, conrelid, contype, oid
ORDER BY
    conrelid::regclass::text, contype DESC;
"""

# PostgreSQL query to get enum types in a schema
POSTGRES_ENUM_TYPES_QUERY = """
SELECT t.typname AS type_name,
       t.typnamespace::regnamespace AS namespace,
       t.typowner::regrole AS owner,
       t.typcategory AS category,
       t.typisdefined AS is_defined,
       t.typtype AS type,
       array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
FROM pg_type t
LEFT JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typtype IN ('d', 'c', 'e', 'r')
GROUP BY t.typname, t.typnamespace, t.typowner, t.typcategory, t.typisdefined, t.typtype
ORDER BY t.typnamespace, t.typname;
"""

# PostgreSQL query to map columns to user-defined types
POSTGRES_USER_DEFINED_TYPE_MAPPING_QUERY = """
SELECT a.attname AS column_name,
       c.relname AS table_name,
       t.typnamespace::regnamespace AS namespace,
       t.typname AS type_name,
       t.typtype AS type_category,
       CASE t.typtype
         WHEN 'd' THEN 'Domain'
         WHEN 'c' THEN 'Composite'
         WHEN 'e' THEN 'Enum'
         WHEN 'r' THEN 'Range'
         ELSE 'Other'
       END AS type_description
FROM pg_attribute a
JOIN pg_class c ON a.attrelid = c.oid
JOIN pg_type t ON a.atttypid = t.oid
WHERE c.relkind = 'r' -- Only look at ordinary tables
  AND NOT a.attisdropped; -- Skip dropped (deleted) columns
"""

# Regular expression for matching PostgreSQL connection URLs
POSTGRES_SQL_CONN_REGEX = (
    r'(postgresql|postgres)://([^:@\s]*(?::[^@\s]*)?@)?(?P<server>[^/\?\s:]+)(:\d+)?(/[^?\s]*)?(\?[^\s]*)?$'
)
