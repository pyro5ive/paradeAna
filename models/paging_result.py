# abstraction/paging_result.py

from dataclasses import dataclass
from typing import Any
from typing import Optional


@dataclass
class PagingResult:
    requested_start: str
    requested_end: str
    returned_count: int
    is_saturated: bool
    payload: dict[str, Any]
    response_text: str
    next_end_date: Optional[str]
    is_complete: bool
#--------------------------#