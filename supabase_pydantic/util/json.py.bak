import decimal
import json
from datetime import date, datetime
from typing import Any


class CustomJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for encoding decimal and datetime."""

    def default(self, o: object) -> Any:
        """Encode decimal and datetime objects."""
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)
