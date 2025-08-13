import decimal
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any


@dataclass
class AsDictParent:
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


class CustomJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for encoding decimal and datetime."""

    def default(self, o: object) -> Any:
        """Encode decimal and datetime objects."""
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)
