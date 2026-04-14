import logging
from typing import Any

import requests

from abstraction.api_client_base import ApiClientBase
from models.api_call_result import ApiCallResult


class CrimeApiClient(ApiClientBase):
    """Executes the API request and returns normalized results."""

    def __init__(self, url: str, bearer_token: str, timeout_seconds: int = 120, logger: logging.Logger | None = None) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.logger = logger or logging.getLogger(f"{__name__}.CrimeApiClient")
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}"
        }
    #--------------------------#

    def execute(self, payload: dict[str, Any]) -> ApiCallResult:
        self.logger.info("Executing API request")

        response: requests.Response = requests.post(
            url=self.url,
            headers=self.headers,
            json=payload,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()

        response_text: str = response.text
        response_json: Any = response.json()
        returned_rows: list[Any] = self.extract_rows(response_json)
        returned_count: int = len(returned_rows)

        self.logger.info("API returned %s rows", returned_count)

        return ApiCallResult(
            payload=payload,
            response_text=response_text,
            response_json=response_json,
            returned_count=returned_count
        )
    #--------------------------#

    def extract_rows(self, response_json: Any) -> list[Any]:
        if isinstance(response_json, list):
            return response_json

        if isinstance(response_json, dict):
            for key in ("data", "results", "rows"):
                value: Any = response_json.get(key)
                if isinstance(value, list):
                    return value

        raise ValueError("Could not find row array in API response. Update extract_rows().")
    #--------------------------#