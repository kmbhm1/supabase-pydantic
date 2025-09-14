from dataclasses import dataclass


@dataclass
class EnumInfo:
    name: str  # The name of the enum type in the DB
    values: list[str]  # The possible values for the enum
    schema: str = 'public'  # The schema, defaulting to 'public'

    def python_class_name(self) -> str:
        """Converts DB enum name to PascalCase for Python class, prefixed by schema.

        Handles various input formats:
        - snake_case: 'order_status' -> 'OrderStatusEnum'
        - camelCase: 'thirdType' -> 'ThirdTypeEnum'
        - PascalCase: 'FourthType' -> 'FourthTypeEnum'
        - mixed: 'Fifth_Type' -> 'FifthTypeEnum'
        - with leading underscore: '_first_type' -> 'FirstTypeEnum'

        Final class name is prefixed by schema: 'public.order_status' -> 'PublicOrderStatusEnum'
        """
        # Handle empty name edge case
        if not self.name:
            return f'{self.schema.capitalize()}Enum'

        # Remove leading underscore if present (for PostgreSQL compatibility)
        clean_name = self.name
        if clean_name.startswith('_'):
            clean_name = clean_name[1:]

        # Special case: if the name is already PascalCase or camelCase without underscores
        if '_' not in clean_name and any(c.isupper() for c in clean_name):
            # Ensure first character is uppercase
            class_name = clean_name[0].upper() + clean_name[1:] + 'Enum'
        else:
            # Standard snake_case processing
            class_name = ''.join(word.capitalize() for word in clean_name.split('_')) + 'Enum'

        # Add schema prefix
        return f'{self.schema.capitalize()}{class_name}'

    def python_member_name(self, value: str) -> str:
        """Converts enum value to a valid Python identifier.

        e.g., 'pending_new' -> 'pending_new'
        """
        return value.lower()
