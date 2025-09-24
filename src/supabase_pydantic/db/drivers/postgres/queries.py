TABLES_QUERY = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s
"""

COLUMNS_QUERY = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
"""

SCHEMAS_QUERY = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
"""

GET_TABLE_COLUMN_DETAILS = """
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
    c.identity_generation,
    c.udt_name,
    CASE
        WHEN c.data_type = 'ARRAY' THEN pg_catalog.format_type(e.oid, NULL)
        ELSE NULL
    END AS array_element_type,
    pgd.description
FROM
    information_schema.columns AS c
JOIN
    information_schema.tables AS t ON c.table_name = t.table_name AND c.table_schema = t.table_schema
LEFT JOIN pg_type e
    ON e.typname = c.udt_name
LEFT JOIN pg_catalog.pg_class cls
    ON cls.relname = c.table_name
   AND cls.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = c.table_schema)
LEFT JOIN pg_catalog.pg_description pgd
    ON pgd.objoid = cls.oid
   AND pgd.objsubid = c.ordinal_position
WHERE
    c.table_schema = %s
    AND (t.table_type = 'BASE TABLE' OR t.table_type = 'VIEW')
ORDER BY
    c.table_schema, c.table_name, c.ordinal_position;
"""

GET_CONSTRAINTS = """
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

GET_USER_DEFINED_TYPES = """
SELECT typname AS type_name,
       typnamespace::regnamespace AS namespace,
       typowner::regrole AS owner,
       typcategory AS category,
       typisdefined AS is_defined,
       typtype AS type,
       typinput::regproc AS input_function,
       typoutput::regproc AS output_function,
       typreceive::regproc AS receive_function,
       typsend::regproc AS send_function,
       typlen AS length,
       typbyval AS by_value,
       typalign AS alignment,
       typdelim AS delimiter,
       typrelid::regclass AS related_table,
       typelem::regtype AS element_type,
       typcollation::regcollation AS collation
FROM pg_type
WHERE typtype IN ('d', 'c', 'e', 'r')  -- d: domain, c: composite, e: enum, r: range
ORDER BY typnamespace, typname;
"""

GET_ENUM_TYPES = """
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

GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING = """
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
WHERE c.relkind IN ('r', 'v') -- Only look at ordinary tables and views
  AND NOT a.attisdropped; -- Skip dropped (deleted) columns
"""
