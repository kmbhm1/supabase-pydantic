import decimal
import json
from datetime import date, datetime


class CustomJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for encoding decimal and datetime."""

    def default(self, o):  # noqa: D102
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)
