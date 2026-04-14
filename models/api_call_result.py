# abstraction/api_call_result.py

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiCallResult:
    payload: dict[str, Any]
    response_text: str
    response_json: Any
    returned_count: int
#--------------------------#