"""Abstract base class for constraint marshaling."""

from abc import ABC, abstractmethod

from supabase_pydantic.db.models import TableInfo


class BaseConstraintMarshaler(ABC):
    """Abstract base class for constraint data marshaling."""

    @abstractmethod
    def parse_foreign_key(self, constraint_def: str) -> tuple[str, str, str] | None:
        """Parse foreign key definition from database-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            Tuple containing (source_column, target_table, target_column) or None.
        """
        pass

    @abstractmethod
    def parse_unique_constraint(self, constraint_def: str) -> list[str]:
        """Parse unique constraint from database-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            List of column names in the unique constraint.
        """
        pass

    @abstractmethod
    def parse_check_constraint(self, constraint_def: str) -> str:
        """Parse check constraint from database-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            Parsed check constraint expression.
        """
        pass

    @abstractmethod
    def add_constraints_to_table_details(
        self, tables: dict[tuple[str, str], TableInfo], constraint_data: list[tuple], schema: str
    ) -> None:
        """Add constraint information to table details.

        Args:
            tables: Dictionary of table information objects.
            constraint_data: Raw constraint data from database.
            schema: Schema name.
        """
        pass
