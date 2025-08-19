"""MySQL schema reader implementation."""

from typing import Any

from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader


class MySQLSchemaReader(BaseSchemaReader):
    """MySQL schema reader implementation."""

    def get_schemas(self, connection: Any) -> list[tuple[str]]:
        """Get all database schemas.

        Args:
            connection: MySQL database connection

        Returns:
            List of schema names as tuples
        """
        query = "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')"  # noqa: E501
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            # Convert dict results to tuples to match PostgreSQL interface
            return [(row['SCHEMA_NAME'],) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def get_tables(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get all tables in a schema.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of table information
        """
        query = """
        SELECT
            TABLE_NAME,
            TABLE_SCHEMA AS schema_name,
            TABLE_TYPE,
            TABLE_COMMENT
        FROM
            information_schema.TABLES
        WHERE
            TABLE_SCHEMA = %s
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            result = cursor.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cursor.close()

    def get_columns(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get all columns for all tables in a schema.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of column information
        """
        query = """
        SELECT
            c.TABLE_SCHEMA AS schema,
            c.TABLE_NAME AS table_name,
            c.COLUMN_NAME AS column_name,
            c.COLUMN_DEFAULT AS default_value,
            c.IS_NULLABLE AS is_nullable,
            c.DATA_TYPE AS data_type,
            c.CHARACTER_MAXIMUM_LENGTH AS max_length,
            t.TABLE_TYPE AS table_type,
            c.EXTRA AS extra_info,
            c.COLUMN_TYPE AS column_type,
            NULL AS array_element_type  -- MySQL doesn't have native arrays like PostgreSQL
        FROM
            information_schema.COLUMNS c
        JOIN
            information_schema.TABLES t
        ON
            c.TABLE_SCHEMA = t.TABLE_SCHEMA AND c.TABLE_NAME = t.TABLE_NAME
        WHERE
            c.TABLE_SCHEMA = %s
        ORDER BY
            c.TABLE_NAME, c.ORDINAL_POSITION
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            result = cursor.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cursor.close()

    def get_constraints(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get all constraints for all tables in a schema.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of constraint information
        """
        query = """
        SELECT
            tc.CONSTRAINT_NAME AS constraint_name,
            tc.TABLE_NAME AS table_name,
            tc.CONSTRAINT_TYPE AS constraint_type,
            kcu.COLUMN_NAME AS column_name,
            GROUP_CONCAT(kcu.COLUMN_NAME ORDER BY kcu.ORDINAL_POSITION) AS column_list
        FROM
            information_schema.TABLE_CONSTRAINTS tc
        JOIN
            information_schema.KEY_COLUMN_USAGE kcu
        ON
            tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            AND tc.TABLE_NAME = kcu.TABLE_NAME
        WHERE
            tc.TABLE_SCHEMA = %s
        GROUP BY
            tc.CONSTRAINT_NAME, tc.TABLE_NAME, tc.CONSTRAINT_TYPE, kcu.COLUMN_NAME
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            result = cursor.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cursor.close()

    def get_foreign_keys(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get all foreign keys for all tables in a schema.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of foreign key information
        """
        query = """
        SELECT
            kcu1.CONSTRAINT_NAME AS constraint_name,
            kcu1.TABLE_NAME AS table_name,
            kcu1.COLUMN_NAME AS column_name,
            kcu1.REFERENCED_TABLE_NAME AS foreign_table_name,
            kcu1.REFERENCED_COLUMN_NAME AS foreign_column_name,
            rc.UPDATE_RULE AS update_rule,
            rc.DELETE_RULE AS delete_rule
        FROM
            information_schema.KEY_COLUMN_USAGE kcu1
        JOIN
            information_schema.REFERENTIAL_CONSTRAINTS rc
        ON
            kcu1.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
            AND kcu1.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
        WHERE
            kcu1.TABLE_SCHEMA = %s
            AND kcu1.REFERENCED_TABLE_SCHEMA IS NOT NULL
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            result = cursor.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cursor.close()

    def get_user_defined_types(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get all user-defined types in a schema.

        MySQL doesn't have PostgreSQL-style user-defined types or ENUMs as separate objects,
        but we return ENUM column definitions.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of enum type information
        """
        query = """
        SELECT
            c.COLUMN_NAME AS type_name,
            c.TABLE_SCHEMA AS namespace,
            'SYSTEM' AS owner,
            'E' AS category,
            'YES' AS is_defined,
            'e' AS type_code,
            SUBSTRING(c.COLUMN_TYPE, 6, LENGTH(c.COLUMN_TYPE) - 6) AS enum_values
        FROM
            information_schema.COLUMNS c
        WHERE
            c.TABLE_SCHEMA = %s
            AND c.COLUMN_TYPE LIKE 'enum(%'
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            results = cursor.fetchall()
            if not isinstance(results, list):
                return []

            # Process enum values string into proper format
            for result in results:
                if 'enum_values' in result and result['enum_values']:
                    # MySQL enum values are stored like: 'value1','value2','value3'
                    # Convert to array format like PostgreSQL
                    values_str = result['enum_values']
                    # Remove outer quotes if present
                    if values_str.startswith("'") and values_str.endswith("'"):
                        values_str = values_str[1:-1]
                    # Split by commas and remove quotes from each value
                    values = [v.strip("'") for v in values_str.split("','")]
                    result['enum_values'] = values
            return results
        finally:
            cursor.close()

    def get_type_mappings(self, connection: Any, schema: str) -> list[dict[Any, Any]]:
        """Get column to user-defined type mappings.

        MySQL doesn't have PostgreSQL-style type mappings, but we map ENUM columns.

        Args:
            connection: MySQL database connection
            schema: Schema name

        Returns:
            List of type mapping information
        """
        query = """
        SELECT
            c.COLUMN_NAME,
            c.TABLE_NAME,
            c.TABLE_SCHEMA AS namespace,
            c.COLUMN_NAME AS type_name,
            'E' AS type_category,
            c.COLUMN_COMMENT AS type_description
        FROM
            information_schema.COLUMNS c
        WHERE
            c.TABLE_SCHEMA = %s
            AND c.COLUMN_TYPE LIKE 'enum(%'
        """
        cursor = connection.cursor()
        try:
            cursor.execute(query, (schema,))
            result = cursor.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cursor.close()
