"""MySQL-specific constants."""

# Maps constraint types to their string representations
MYSQL_CONSTRAINT_TYPE_MAP = {
    'PRIMARY KEY': 'PRIMARY KEY',
    'FOREIGN KEY': 'FOREIGN KEY',
    'UNIQUE': 'UNIQUE',
    'CHECK': 'CHECK',
}

# Maps MySQL data types to their Python equivalents
MYSQL_USER_DEFINED_TYPE_MAP = {'ENUM': 'ENUM', 'SET': 'SET'}
