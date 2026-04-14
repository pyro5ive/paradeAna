# abstraction/paging_coordinator_base.py

from abc import ABC
from abc import abstractmethod

from models.paging_result import PagingResult


class PagingCoordinatorBase(ABC):
    """Abstract coordinator that produces the next paging result."""

    @abstractmethod
    def collect_next(self, overall_start_text: str, current_end_text: str) -> PagingResult:
        raise NotImplementedError()
#--------------------------#