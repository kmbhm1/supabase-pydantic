from dataclasses import dataclass


@dataclass
class EnumInfo:
    name: str  # The name of the enum type in the DB
    values: list[str]  # The possible values for the enum
    schema: str = 'public'  # The schema, defaulting to 'public'

    def python_class_name(self) -> str:
        """Converts DB enum name to PascalCase for Python class, prefixed by schema.

        e.g., 'order_status' in 'public' -> 'PublicOrderStatusEnum'
        """
        class_name = ''.join(word.capitalize() for word in self.name.split('_')) + 'Enum'
        # TODO: decide whether to keep underscores in prefix for original enum; issue #84
        # print(f'Enum info: {self.name}, {class_name}')
        return f'{self.schema.capitalize()}{class_name}'

    def python_member_name(self, value: str) -> str:
        """Converts enum value to a valid Python identifier.

        e.g., 'pending_new' -> 'pending_new'
        """
        return value.lower()
