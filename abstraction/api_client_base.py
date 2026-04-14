# abstraction/api_client_base.py

from abc import ABC
from abc import abstractmethod
from typing import Any

from models.api_call_result import  ApiCallResult


class ApiClientBase(ABC):
    """Abstract API client for executing requests."""

    @abstractmethod
    def execute(self, payload: dict[str, Any]) -> ApiCallResult:
        raise NotImplementedError()
    #--------------------------#