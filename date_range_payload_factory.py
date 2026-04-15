import copy
import json
import logging
from datetime import datetime
from typing import Any

from abstraction.payload_factory_base import PayloadFactoryBase


class DateRangePayloadFactory(PayloadFactoryBase):
    """Creates API payloads for a requested date range."""

    def __init__(
        this,
        payloadFilePath: str
    ) -> None:
        this.payloadFilePath = payloadFilePath
        this.logger = logging.getLogger(__name__ + ".DateRangePayloadFactory")
        this.basePayload = this.load_payload_file(payloadFilePath)
    #--------------------------#

    def load_payload_file(this, payloadFilePath: str) -> dict[str, Any]:
        fileHandle = open(payloadFilePath, "r", encoding="utf-8")

        try:
            payloadData: dict[str, Any] = json.load(fileHandle)
            return payloadData
        finally:
            fileHandle.close()
    #--------------------------#

    def format_api_date(this, value: datetime) -> str:
        return value.strftime("%m/%d/%Y")
    #--------------------------#

    def build_payload(this, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        payload: dict[str, Any] = copy.deepcopy(this.basePayload)

        payload["date"]["start"] = this.format_api_date(start_date)
        payload["date"]["end"] = this.format_api_date(end_date)

        this.logger.debug(
            "Built payload for range %s -> %s",
            payload["date"]["start"],
            payload["date"]["end"]
        )

        return payload
    #--------------------------#