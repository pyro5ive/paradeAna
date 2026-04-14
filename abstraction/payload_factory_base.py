# abstraction/payload_factory_base.py

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any


class PayloadFactoryBase(ABC):
    """Abstract factory for building API payloads."""

    @abstractmethod
    def build_payload(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        raise NotImplementedError()
#--------------------------#