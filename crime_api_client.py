import logging
from typing import Any

import requests

from abstraction.api_client_base import ApiClientBase
from models.api_call_result import ApiCallResult


class CrimeApiClient(ApiClientBase):
    """Executes the API request and returns normalized results."""

    def __init__(this, url: str, bearer_token: str,  timeout_seconds: int = 120) -> None:
        this.url = url
        this.timeout_seconds = timeout_seconds
        this.logger = logging.getLogger(__name__ + ".CrimeApiClient")
        this.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + bearer_token
        }
    #--------------------------#

    def execute(this, payload: dict[str, Any]) -> ApiCallResult:
        this.logger.info("Executing API request")

        response: requests.Response = requests.post(url=this.url, headers=this.headers, json=payload, timeout=this.timeout_seconds )
        response.raise_for_status()

        response_text: str = response.text
        response_json: Any = response.json()
        returned_rows: list[Any] = this.extract_rows(response_json)
        returned_count: int = len(returned_rows)

        this.logger.info("API returned %s rows", returned_count)

        return ApiCallResult(
            payload=payload,
            response_text=response_text,
            response_json=response_json,
            returned_count=returned_count
        )
    #--------------------------#

    def extract_rows(this, response_json: Any) -> list[Any]:
        if isinstance(response_json, dict):
            dataLevel: Any = response_json.get("data")

            if isinstance(dataLevel, dict):
                grid: Any = dataLevel.get("grid")

                if isinstance(grid, dict):
                    eve: Any = grid.get("eve")

                    if isinstance(eve, list):
                        return eve

        raise ValueError("Could not find data.grid.eve in API response.")
    # --------------------------#