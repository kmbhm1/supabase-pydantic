#!/usr/bin/env python
"""
Vulture whitelist file.

This file contains definitions of symbols that Vulture reports as unused,
but are actually used in the codebase (typically via imports for type hints,
side effects, or used by other modules dynamically).

See: https://github.com/jendrikseipp/vulture#handling-false-positives
"""

# ------------------------------------------------------------------------------
# Core modules
# ------------------------------------------------------------------------------
ModelGenerationType  # unused class (src/supabase_pydantic/core/constants.py:27)
MAIN  # unused variable (src/supabase_pydantic/core/constants.py:29)

# Core writers methods - these are part of the API contract
write_operational_class  # unused method (src/supabase_pydantic/core/writers/abstract.py:62)
write_operational_class  # unused method (src/supabase_pydantic/core/writers/pydantic.py:437)
write_operational_class  # unused method (src/supabase_pydantic/core/writers/sqlalchemy.py:303)

# ------------------------------------------------------------------------------
# Database modules
# ------------------------------------------------------------------------------
DatabaseUserDefinedType  # unused class (src/supabase_pydantic/db/constants.py:20)
DOMAIN  # unused variable (src/supabase_pydantic/db/constants.py:23)
COMPOSITE  # unused variable (src/supabase_pydantic/db/constants.py:24)
ENUM  # unused variable (src/supabase_pydantic/db/constants.py:25)
RANGE  # unused variable (src/supabase_pydantic/db/constants.py:26)
POSTGRES_SQL_CONN_REGEX  # unused variable (src/supabase_pydantic/db/constants.py:31)

# Used in type mappings and marshalers
MYSQL_CONSTRAINT_TYPE_MAP  # unused variable (src/supabase_pydantic/db/drivers/mysql/constants.py:4)
MYSQL_USER_DEFINED_TYPE_MAP  # unused variable (src/supabase_pydantic/db/drivers/mysql/constants.py:12)
USER_DEFINED_TYPE_MAP  # unused variable (src/supabase_pydantic/db/drivers/postgres/constants.py:5)
GET_USER_DEFINED_TYPES  # unused variable (src/supabase_pydantic/db/drivers/postgres/queries.py:91)

# Database connector methods - part of the interface contract
validate_connection_params  # unused method (src/supabase_pydantic/db/abstract/base_connector.py:75)
validate_connection_params  # unused method (src/supabase_pydantic/db/connectors/mysql/connector.py:252)
validate_connection_params  # unused method (src/supabase_pydantic/db/connectors/postgres/connector.py:43)

# Database marshaler methods - required for interface implementations
process_array_type  # unused method (src/supabase_pydantic/db/marshalers/abstract/base_column_marshaler.py:48)
process_array_type  # unused method (src/supabase_pydantic/db/marshalers/mysql/column.py:46)
process_array_type  # unused method (src/supabase_pydantic/db/marshalers/postgres/column.py:35)

# Constraint marshaler methods - required for interface implementations
parse_foreign_key  # unused method (src/supabase_pydantic/db/marshalers/abstract/base_constraint_marshaler.py:11)
parse_unique_constraint  # unused method (src/supabase_pydantic/db/marshalers/abstract/base_constraint_marshaler.py:23)
parse_check_constraint  # unused method (src/supabase_pydantic/db/marshalers/abstract/base_constraint_marshaler.py:35)
parse_foreign_key  # unused method (src/supabase_pydantic/db/marshalers/mysql/constraints.py:23)
parse_unique_constraint  # unused method (src/supabase_pydantic/db/marshalers/mysql/constraints.py:48)
parse_check_constraint  # unused method (src/supabase_pydantic/db/marshalers/mysql/constraints.py:68)
parse_foreign_key  # unused method (src/supabase_pydantic/db/marshalers/postgres/constraints.py:16)
parse_unique_constraint  # unused method (src/supabase_pydantic/db/marshalers/postgres/constraints.py:21)
parse_check_constraint  # unused method (src/supabase_pydantic/db/marshalers/postgres/constraints.py:29)
_determine_relationship_types  # unused method (src/supabase_pydantic/db/marshalers/mysql/relationship.py:59)

# Database models classes and fields - used for typing and serialization
UserDefinedType  # unused class (src/supabase_pydantic/db/models.py:14)
input_function  # unused variable (src/supabase_pydantic/db/models.py:22)
output_function  # unused variable (src/supabase_pydantic/db/models.py:23)
receive_function  # unused variable (src/supabase_pydantic/db/models.py:24)
send_function  # unused variable (src/supabase_pydantic/db/models.py:25)
length  # unused variable (src/supabase_pydantic/db/models.py:26)
by_value  # unused variable (src/supabase_pydantic/db/models.py:27)
alignment  # unused variable (src/supabase_pydantic/db/models.py:28)
delimiter  # unused variable (src/supabase_pydantic/db/models.py:29)
collation  # unused variable (src/supabase_pydantic/db/models.py:32)
unique_partners  # unused variable (src/supabase_pydantic/db/models.py:81)
generated_data  # unused variable (src/supabase_pydantic/db/models.py:180)
unique_partners  # unused attribute (src/supabase_pydantic/db/marshalers/constraints.py:87)

# Database models methods - used for type-specific operations
orm_imports  # unused method (src/supabase_pydantic/db/models.py:108)
orm_datatype  # unused method (src/supabase_pydantic/db/models.py:118)
is_user_defined_type  # unused method (src/supabase_pydantic/db/models.py:127)
aliasing_in_columns  # unused method (src/supabase_pydantic/db/models.py:198)
primary_is_composite  # unused method (src/supabase_pydantic/db/models.py:214)

# Connection parameters models and validators
DirectConnectionParams  # unused class (src/supabase_pydantic/db/models.py:284)
URLConnectionParams  # unused class (src/supabase_pydantic/db/models.py:294)
validate_db_url  # unused function (src/supabase_pydantic/db/models.py:315)
validate_port  # unused function (src/supabase_pydantic/db/models.py:324)
model_config  # unused variable (src/supabase_pydantic/db/models.py:356)
validate_port  # unused function (src/supabase_pydantic/db/models.py:369)
model_config  # unused variable (src/supabase_pydantic/db/models.py:399)

# Database graph utility
build_dependency_graph  # unused function (src/supabase_pydantic/db/graph.py:11)
get_database_name_from_url  # unused function (src/supabase_pydantic/db/utils/url_parser.py:34)

# CLI & utility
check_readiness  # unused function (src/supabase_pydantic/cli/common.py:15)
as_dict  # unused method (src/supabase_pydantic/utils/serialization.py:10)
get_enum_member_from_string  # unused function (src/supabase_pydantic/utils/types.py:9)
handlers  # unused attribute (src/supabase_pydantic/utils/logging.py:90)

# These appear to be deprecated and can likely be removed if no longer needed
overwrite_existing_files  # unused variable (src/supabase_pydantic/utils/constants.py:8)
nullify_base_schema  # unused variable (src/supabase_pydantic/utils/constants.py:9)
supabase_pydantic  # unused variable (src/supabase_pydantic/utils/constants.py:16)
STD_PYDANTIC_FILENAME  # unused variable (src/supabase_pydantic/utils/constants.py:20)
STD_SQLALCHEMY_FILENAME  # unused variable (src/supabase_pydantic/utils/constants.py:21)
STD_SEED_DATA_FILENAME  # unused variable (src/supabase_pydantic/utils/constants.py:22)
