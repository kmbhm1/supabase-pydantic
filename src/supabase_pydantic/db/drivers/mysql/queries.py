"""MySQL-specific queries for schema information retrieval."""

TABLES_QUERY = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s
"""

COLUMNS_QUERY = """
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable,
    character_maximum_length,
    column_type,
    CASE
        WHEN extra LIKE '%auto_increment%' THEN 'IDENTITY'
        ELSE NULL
    END as identity_generation
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
ORDER BY ordinal_position
"""

SCHEMAS_QUERY = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
"""

FOREIGN_KEYS_QUERY = """
SELECT
    tc.constraint_schema AS table_schema,
    tc.table_name AS table_name,
    kcu.column_name AS column_name,
    kcu.referenced_table_schema AS foreign_table_schema,
    kcu.referenced_table_name AS foreign_table_name,
    kcu.referenced_column_name AS foreign_column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
ON
    tc.constraint_name = kcu.constraint_name
    AND tc.constraint_schema = kcu.constraint_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.constraint_schema = %s;
"""

GET_ALL_PUBLIC_TABLES_AND_COLUMNS = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.column_default,
    c.is_nullable,
    c.data_type,
    c.character_maximum_length,
    t.table_type,
    CASE
        WHEN c.extra LIKE '%auto_increment%' THEN 'IDENTITY'
        ELSE NULL
    END as identity_generation,
    c.data_type as udt_name,
    NULL as array_element_type,
    c.column_comment as description
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

CONSTRAINTS_QUERY = """
SELECT
    tc.constraint_name AS constraint_name,
    tc.table_name AS table_name,
    GROUP_CONCAT(kcu.column_name ORDER BY kcu.ordinal_position) AS columns,
    tc.constraint_type AS constraint_type,
    CONCAT(tc.constraint_type, ' (', GROUP_CONCAT(kcu.column_name ORDER BY kcu.ordinal_position), ')') AS constraint_definition
FROM
    information_schema.table_constraints tc
JOIN
    information_schema.key_column_usage kcu
ON
    tc.constraint_catalog = kcu.constraint_catalog
    AND tc.constraint_schema = kcu.constraint_schema
    AND tc.constraint_name = kcu.constraint_name
    AND tc.table_name = kcu.table_name
WHERE
    tc.constraint_schema = %s
GROUP BY
    tc.constraint_name, tc.constraint_type, tc.table_name
ORDER BY
    tc.table_name, tc.constraint_type DESC;
"""  # noqa: E501

ENUMS_QUERY = """
SELECT
    -- Enum type name (use column_name + '_enum' to create a unique type name)
    CONCAT(c.column_name, '_enum') AS type_name,
    -- Namespace is the schema name
    c.table_schema AS namespace,
    -- Owner - MySQL doesn't track owner the same way, use current user
    'mysql_user' AS owner,
    -- Category - use 'E' for enum like PostgreSQL
    'E' AS category,
    -- Is defined - always true for MySQL enums
    TRUE AS is_defined,
    -- Type - use 'e' for enum like PostgreSQL
    'e' AS type,
    -- Enum values as a string that can be parsed as an array
    -- Extract values from enum('value1','value2') format
    SUBSTRING(
        COLUMN_TYPE,
        LOCATE('enum(', COLUMN_TYPE) + 5,
        LENGTH(COLUMN_TYPE) - LOCATE('enum(', COLUMN_TYPE) - 6
    ) AS enum_values
FROM
    information_schema.columns c
WHERE
    c.table_schema = %s
    AND c.column_type LIKE 'enum%';
"""

USER_DEFINED_TYPES_QUERY = """
SELECT
    c.column_name AS column_name,
    c.table_name AS table_name,
    c.table_schema AS namespace,
    c.data_type AS type_name,
    CASE
        WHEN c.data_type = 'enum' THEN 'e'
        WHEN c.data_type = 'set' THEN 's'
        ELSE 'o'
    END AS type_category,
    CASE
        WHEN c.data_type = 'enum' THEN 'Enum'
        WHEN c.data_type = 'set' THEN 'Set'
        ELSE 'Other'
    END AS type_description
FROM
    information_schema.columns c
WHERE
    c.table_schema = %s
    AND (c.data_type = 'enum' OR c.data_type = 'set');
"""
