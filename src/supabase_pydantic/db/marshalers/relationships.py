import logging

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.column import standardize_column_name
from supabase_pydantic.db.models import ForeignKeyInfo, RelationshipInfo, TableInfo

# Get Logger
logger = logging.getLogger(__name__)


def add_relationships_to_table_details(tables: dict, fk_details: list) -> None:
    """Add relationships to the table details."""
    # Process relationships
    for row in fk_details:
        (
            table_schema,
            table_name,
            column_name,
            foreign_table_schema,
            foreign_table_name,
            foreign_column_name,
            constraint_name,
        ) = row
        table_key = (table_schema, table_name)
        foreign_table_key = (foreign_table_schema, foreign_table_name)

        # Skip if either table doesn't exist
        if table_key not in tables or foreign_table_key not in tables:
            continue

        table = tables[table_key]
        foreign_table = tables[foreign_table_key]

        # If this is a bridge table, create MANY_TO_MANY relationships between the tables it connects
        if table.is_bridge:
            # Get all foreign keys in the bridge table
            bridge_fks = table.foreign_keys
            # For each pair of tables connected by the bridge table
            for i, fk1 in enumerate(bridge_fks):
                for fk2 in bridge_fks[i + 1 :]:  # noqa: E203
                    # Add MANY_TO_MANY relationships between the connected tables
                    # Use the bridge table's schema since all tables are in the same schema
                    table1_key = (table.schema, fk1.foreign_table_name)
                    table2_key = (table.schema, fk2.foreign_table_name)
                    if table1_key in tables and table2_key in tables:
                        # Add relationship from table1 to table2
                        tables[table1_key].relationships.append(
                            RelationshipInfo(
                                table_name=table1_key[1],
                                related_table_name=fk2.foreign_table_name,
                                relation_type=RelationType.MANY_TO_MANY,
                            )
                        )
                        # Add relationship from table2 to table1
                        tables[table2_key].relationships.append(
                            RelationshipInfo(
                                table_name=table2_key[1],
                                related_table_name=fk1.foreign_table_name,
                                relation_type=RelationType.MANY_TO_MANY,
                            )
                        )

        # For non-bridge tables, determine the relationship type
        fk_columns = [fk for fk in table.foreign_keys if fk.foreign_table_name == foreign_table_name]
        if len(fk_columns) == 1:
            # One-to-Many or One-to-One
            is_source_unique = any(col.name == column_name and (col.is_unique or col.primary) for col in table.columns)
            is_target_unique = any(
                col.name == foreign_column_name and (col.is_unique or col.primary) for col in foreign_table.columns
            )

            if is_source_unique and is_target_unique:
                relation_type = RelationType.ONE_TO_ONE
            else:
                relation_type = RelationType.ONE_TO_MANY
        else:
            # Many-to-Many
            relation_type = RelationType.MANY_TO_MANY

        # Add relationship to both tables
        if table_key in tables:
            tables[table_key].relationships.append(
                RelationshipInfo(
                    table_name=table_key[1],
                    related_table_name=foreign_table_key[1],
                    relation_type=relation_type,
                )
            )
        if foreign_table_key in tables:
            tables[foreign_table_key].relationships.append(
                RelationshipInfo(
                    table_name=foreign_table_key[1],
                    related_table_name=table_key[1],
                    relation_type=relation_type,
                )
            )


def determine_relationship_type(
    source_table: TableInfo, target_table: TableInfo, fk: ForeignKeyInfo
) -> tuple[RelationType, RelationType]:
    """Determine the relationship type between two tables based on their constraints.

    Args:
        source_table: The table containing the foreign key
        target_table: The table being referenced by the foreign key
        fk: The foreign key information

    Returns:
        A tuple of (forward_type, reverse_type) representing the relationship in both directions
    """
    # Check primary key constraints
    source_primary_constraints = [
        c for c in source_table.constraints if c.raw_constraint_type == 'p' and fk.column_name in c.columns
    ]
    target_primary_constraints = [
        c for c in target_table.constraints if c.raw_constraint_type == 'p' and fk.foreign_column_name in c.columns
    ]

    # Check if columns are sole primary keys
    is_source_sole_primary = any(len(c.columns) == 1 for c in source_primary_constraints)
    is_target_sole_primary = any(len(c.columns) == 1 for c in target_primary_constraints)

    # Check uniqueness constraints
    is_source_unique = is_source_sole_primary or any(
        col.name == fk.column_name and col.is_unique for col in source_table.columns
    )
    is_target_unique = is_target_sole_primary or any(
        col.is_unique and col.name == fk.foreign_column_name for col in target_table.columns
    )

    # Log the analysis
    logger.debug(
        f'Analyzing relationship: {source_table.name}.{fk.column_name} -> {target_table.name}.{fk.foreign_column_name}'
    )
    logger.debug(f'Source uniqueness: {is_source_unique}, Target uniqueness: {is_target_unique}')

    # Determine relationship type
    if is_source_unique and is_target_unique:
        # If both sides are unique, it's a one-to-one relationship
        logger.debug('ONE_TO_ONE: Both sides are unique')
        return RelationType.ONE_TO_ONE, RelationType.ONE_TO_ONE
    elif is_target_unique:
        # If only target is unique, it's many-to-one from source to target
        logger.debug('MANY_TO_ONE: Target is unique, source is not')
        return RelationType.MANY_TO_ONE, RelationType.ONE_TO_MANY
    elif is_source_unique:
        # If only source is unique, it's one-to-many from source to target
        logger.debug('ONE_TO_MANY: Source is unique, target is not')
        return RelationType.ONE_TO_MANY, RelationType.MANY_TO_ONE
    else:
        # If neither side is unique, it's many-to-many
        logger.debug('MANY_TO_MANY: Neither side is unique')
        return RelationType.MANY_TO_MANY, RelationType.MANY_TO_MANY


def analyze_table_relationships(tables: dict) -> None:
    """Analyze table relationships."""
    # Keep track of processed relationships to avoid duplicate analysis
    processed_constraints = set()

    for table in tables.values():
        for fk in table.foreign_keys:
            # Skip if we've already processed this constraint
            if fk.constraint_name in processed_constraints:
                continue

            # Get the foreign table
            foreign_table = next(
                (t for t in tables.values() if t.name == fk.foreign_table_name and t.schema == fk.foreign_table_schema),
                None,
            )
            if not foreign_table:
                continue

            # Determine relationship types for both directions
            forward_type, reverse_type = determine_relationship_type(table, foreign_table, fk)

            # Set the forward relationship type
            fk.relation_type = forward_type

            # Handle the reverse relationship
            existing_fk = next((f for f in foreign_table.foreign_keys if f.constraint_name == fk.constraint_name), None)

            if existing_fk:
                # Update existing reverse foreign key
                existing_fk.relation_type = reverse_type
            else:
                # Create new reverse foreign key
                reverse_fk = ForeignKeyInfo(
                    constraint_name=fk.constraint_name,
                    column_name=fk.foreign_column_name,
                    foreign_table_name=table.name,
                    foreign_column_name=fk.column_name,
                    relation_type=reverse_type,
                )
                foreign_table.foreign_keys.append(reverse_fk)

            # Mark this constraint as processed
            processed_constraints.add(fk.constraint_name)


def is_bridge_table(table: TableInfo) -> bool:
    """Check if the table is a bridge table."""
    logger.debug(f'Analyzing if {table.name} is a bridge table')
    logger.debug(f'Foreign keys: {[fk.column_name for fk in table.foreign_keys]}')

    # Check for at least two foreign keys
    if len(table.foreign_keys) < 2:
        logger.debug('Not a bridge table: Less than 2 foreign keys')
        return False

    # Identify columns that are both primary keys and part of foreign keys
    primary_foreign_keys = [
        col.name
        for col in table.columns
        if col.primary and any(fk.column_name == col.name for fk in table.foreign_keys)
    ]
    logger.debug(f'Primary foreign keys: {primary_foreign_keys}')

    # Check if there are at least two such columns
    if len(primary_foreign_keys) < 2:
        logger.debug('Not a bridge table: Less than 2 primary foreign keys')
        return False

    # Get all primary key columns
    primary_keys = [col.name for col in table.columns if col.primary]
    logger.debug(f'All primary keys: {primary_keys}')

    # Consider the table a bridge table if the primary key is composite and includes at least two foreign key columns
    if len(primary_foreign_keys) == len(primary_keys):
        logger.debug('Is bridge table: All primary keys are foreign keys')
        return True

    logger.debug('Not a bridge table: Some primary keys are not foreign keys')
    return False


def analyze_bridge_tables(tables: dict) -> None:
    """Analyze if each table is a bridge table."""
    for table in tables.values():
        table.is_bridge = is_bridge_table(table)
        if table.is_bridge:
            # Update all foreign key relationships to MANY_TO_MANY
            for fk in table.foreign_keys:
                logger.debug(
                    f'Setting {table.name}.{fk.column_name} -> {fk.foreign_table_name}.{fk.foreign_column_name} to MANY_TO_MANY'  # noqa: E501
                )
                fk.relation_type = RelationType.MANY_TO_MANY


def add_foreign_key_info_to_table_details(tables: dict, fk_details: list) -> None:
    """Add foreign key information to the table details.

    Skips foreign keys where either the source or target table is missing.
    This ensures that all foreign keys have valid relationship types.
    """
    for row in fk_details:
        (
            table_schema,
            table_name,
            column_name,
            foreign_table_schema,
            foreign_table_name,
            foreign_column_name,
            constraint_name,
        ) = row
        table_key = (table_schema, table_name)
        foreign_table_key = (foreign_table_schema, foreign_table_name)

        # Skip if either table is missing
        if table_key not in tables or foreign_table_key not in tables:
            missing_source = table_key not in tables
            missing_target = foreign_table_key not in tables
            if missing_target and not missing_source:
                logger.debug(
                    f'Foreign key {constraint_name} references table {foreign_table_schema}.{foreign_table_name} '
                    f'which is not in the current analysis. If you need complete relationship information, '
                    f'consider including the {foreign_table_schema} schema in your analysis.'
                )
            else:
                logger.debug(
                    f'Skipping foreign key {constraint_name} - missing source table {table_schema}.{table_name}'
                )
            continue

        # Determine relationship type
        relation_type = None
        if table_key in tables and foreign_table_key in tables:
            logger.debug(
                f'Analyzing relationship for {table_key[1]}.{column_name} '
                f'-> {foreign_table_key[1]}.{foreign_column_name}'
            )

            # First check if this is a one-to-one relationship
            # This happens when the foreign key is the only primary key in either table
            is_one_to_one = False
            found_composite_key = False

            # Check if foreign key is the only primary key in source table
            logger.debug(f'Checking constraints in source table {table_key[1]}:')
            for constraint in tables[table_key].constraints:
                logger.debug(f'  - Constraint: {constraint.raw_constraint_type}, columns: {constraint.columns}')
                if constraint.raw_constraint_type == 'p':  # primary key
                    # Check if the foreign key column is part of the primary key
                    if column_name in constraint.columns:
                        # If it's part of a composite key, it should be many-to-one
                        if len(constraint.columns) > 1:
                            logger.debug(f'    Found composite primary key including {column_name}')
                            # Found a composite key, so this must be many-to-one
                            found_composite_key = True
                            break
                        else:
                            logger.debug(f'    Found single primary key constraint on {column_name}')
                            is_one_to_one = True

            # If we found a composite key, it's definitely many-to-one
            if found_composite_key:
                is_one_to_one = False
            # Otherwise check the target table
            elif not is_one_to_one:
                logger.debug(f'Checking constraints in target table {foreign_table_key[1]}:')
                for constraint in tables[foreign_table_key].constraints:
                    logger.debug(f'  - Constraint: {constraint.raw_constraint_type}, columns: {constraint.columns}')
                    if constraint.raw_constraint_type == 'p':  # primary key
                        # Check if the foreign key column is part of the primary key
                        if foreign_column_name in constraint.columns:
                            # If it's part of a composite key, it should be many-to-one
                            if len(constraint.columns) > 1:
                                logger.debug(f'    Found composite primary key including {foreign_column_name}')
                                # Found a composite key, so this must be many-to-one
                                found_composite_key = True
                                break
                            else:
                                logger.debug(f'    Found single primary key constraint on {foreign_column_name}')
                                is_one_to_one = True

            # If we found a composite key in either table, it's many-to-one
            if found_composite_key:
                is_one_to_one = False

            if is_one_to_one:
                relation_type = RelationType.ONE_TO_ONE
                logger.debug('Detected ONE_TO_ONE relationship')
            else:
                # If not one-to-one, check if it's many-to-many
                fk_columns = [
                    fk for fk in tables[table_key].foreign_keys if fk.foreign_table_name == foreign_table_name
                ]
                if len(fk_columns) > 1:
                    relation_type = RelationType.MANY_TO_MANY
                    logger.debug('Detected MANY_TO_MANY relationship (multiple foreign keys to same table)')
                else:
                    # If not one-to-one or many-to-many, then it's a many-to-one relationship
                    # from the perspective of the table with the foreign key
                    relation_type = RelationType.MANY_TO_ONE
                    logger.debug('Detected MANY_TO_ONE relationship (default case)')

        if table_key in tables:
            fk_info = ForeignKeyInfo(
                constraint_name=constraint_name,
                column_name=standardize_column_name(column_name) or column_name,
                foreign_table_name=foreign_table_name,
                foreign_column_name=standardize_column_name(foreign_column_name) or foreign_column_name,
                relation_type=relation_type,
                foreign_table_schema=foreign_table_schema,
            )
            tables[table_key].add_foreign_key(fk_info)
