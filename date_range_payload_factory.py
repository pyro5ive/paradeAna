# implementation/date_range_payload_factory.py

import copy
import logging
from datetime import datetime
from typing import Any
from typing import Optional

from abstraction.payload_factory_base import PayloadFactoryBase


class DateRangePayloadFactory(PayloadFactoryBase):
    """Creates API payloads for a requested date range."""

    def __init__(this, base_payload: dict[str, Any], location_payload: Optional[dict[str, Any]] = None, type_selection_payload: Optional[dict[str, Any]] = None, logger: Optional[logging.Logger] = None) -> None:
        this.base_payload = base_payload
        this.location_payload = location_payload
        this.type_selection_payload = type_selection_payload
        this.logger = logger if logger is not None else logging.getLogger(__name__ + ".DateRangePayloadFactory")
#--------------------------#

    def format_api_date(this, value: datetime) -> str:
        return value.strftime("%m/%d/%Y")
#--------------------------#

    def build_payload(this, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        payload: dict[str, Any] = copy.deepcopy(this.base_payload)

        payload["date"]["start"] = this.format_api_date(start_date)
        payload["date"]["end"] = this.format_api_date(end_date)

        if this.location_payload is not None and "location" in this.location_payload:
            payload["location"] = copy.deepcopy(this.location_payload["location"])

        if this.type_selection_payload is not None and "layers" in this.type_selection_payload:
            payload["layers"] = copy.deepcopy(this.type_selection_payload["layers"])

        this.logger.debug(
            "Built payload for range %s -> %s",
            payload["date"]["start"],
            payload["date"]["end"]
        )

        return payload
#--------------------------#