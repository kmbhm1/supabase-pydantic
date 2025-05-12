"""Core module for supabase-pydantic."""

# Export key constants and types
from src.supabase_pydantic.core.constants import (
    PYDANTIC_TYPE_MAP,
    AppConfig,
    DatabaseConnectionType,
    DatabaseUserDefinedType,
    FrameWorkType,
    ModelGenerationType,
    OrmType,
    RelationType,
    ToolConfig,
    WriterConfig,
)

# Export utility functions
from src.supabase_pydantic.core.file_utils import (
    clean_directories,
    create_directories_if_not_exist,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
)

# Export data models
from src.supabase_pydantic.core.models import (
    AsDictParent,
    ColumnInfo,
    ConstraintInfo,
    EnumInfo,
    ForeignKeyInfo,
    RelationshipInfo,
    SortedColumns,
    TableInfo,
    UserEnumType,
    UserTypeMapping,
)
from src.supabase_pydantic.core.type_utils import (
    adapt_type_map,
    get_enum_member_from_string,
    get_pydantic_type,
    get_relationship_field_type,
    get_sqlalchemy_type,
    to_pascal_case,
)

# Re-export from utils module (during transition)
from src.supabase_pydantic.core.utils import (
    check_readiness,
    format_with_ruff,
    generate_seed_data,
    write_seed_file,
)

__all__ = [
    # Constants and types
    'AppConfig',
    'DatabaseConnectionType',
    'DatabaseUserDefinedType',
    'FrameWorkType',
    'ModelGenerationType',
    'OrmType',
    'PYDANTIC_TYPE_MAP',
    'RelationType',
    'ToolConfig',
    'WriterConfig',
    # Data models
    'AsDictParent',
    'ColumnInfo',
    'ConstraintInfo',
    'EnumInfo',
    'ForeignKeyInfo',
    'RelationshipInfo',
    'SortedColumns',
    'TableInfo',
    'UserEnumType',
    'UserTypeMapping',
    # Utility functions
    'adapt_type_map',
    'check_readiness',
    'clean_directories',
    'create_directories_if_not_exist',
    'format_with_ruff',
    'generate_seed_data',
    'get_enum_member_from_string',
    'get_pydantic_type',
    'get_relationship_field_type',
    'get_sqlalchemy_type',
    'get_standard_jobs',
    'get_working_directories',
    'local_default_env_configuration',
    'to_pascal_case',
    'write_seed_file',
]
