# implementation/date_range_paging_proxy.py

import logging
from datetime import datetime
from datetime import timedelta
from typing import Optional

from abstraction.api_client_base import ApiClientBase
from abstraction.paging_coordinator_base import PagingCoordinatorBase
from abstraction.payload_factory_base import PayloadFactoryBase
from models.api_call_result import ApiCallResult
from models.paging_result import PagingResult


class DateRangePagingProxy(PagingCoordinatorBase):
    """Finds the next best date-range page using reverse date packing."""

    def __init__(this, payload_factory: PayloadFactoryBase, api_client: ApiClientBase, row_cap: int = 500, logger: Optional[logging.Logger] = None) -> None:
        this.payload_factory = payload_factory
        this.api_client = api_client
        this.row_cap = row_cap
        this.logger = logger if logger is not None else logging.getLogger(__name__ + ".DateRangePagingProxy")
    #--------------------------#

    def parse_iso_date(this, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d")
    #--------------------------#

    def format_iso_date(this, value: datetime) -> str:
        return value.strftime("%Y-%m-%d")
    #--------------------------#

    def get_previous_day(this, value: datetime) -> datetime:
        return value - timedelta(days=1)
    #--------------------------#

    def is_safe_count(this, returned_count: int) -> bool:
        return returned_count < this.row_cap
    #--------------------------#

    def is_single_day_range(this, start_date: datetime, end_date: datetime) -> bool:
        return start_date == end_date
    #--------------------------#

    def create_complete_result(this) -> PagingResult:
        return PagingResult(
            requested_start="",
            requested_end="",
            returned_count=0,
            is_saturated=False,
            payload={},
            response_text="",
            next_end_date=None,
            is_complete=True
        )
    #--------------------------#

    def create_paging_result(this, start_date: datetime, end_date: datetime, api_call_result: ApiCallResult, is_saturated: bool, next_end_date: Optional[datetime]) -> PagingResult:
        next_end_date_text: Optional[str] = None

        if next_end_date is not None:
            next_end_date_text = this.format_iso_date(next_end_date)

        return PagingResult(
            requested_start=this.format_iso_date(start_date),
            requested_end=this.format_iso_date(end_date),
            returned_count=api_call_result.returned_count,
            is_saturated=is_saturated,
            payload=api_call_result.payload,
            response_text=api_call_result.response_text,
            next_end_date=next_end_date_text,
            is_complete=False
        )
    #--------------------------#

    def test_range(this, start_date: datetime, end_date: datetime) -> ApiCallResult:
        payload = this.payload_factory.build_payload(start_date, end_date)

        this.logger.info(
            "Testing range %s -> %s",
            this.format_iso_date(start_date),
            this.format_iso_date(end_date)
        )

        result: ApiCallResult = this.api_client.execute(payload)

        this.logger.info(
            "Range %s -> %s returned %s rows",
            this.format_iso_date(start_date),
            this.format_iso_date(end_date),
            result.returned_count
        )

        return result
    #--------------------------#

    def collect_next(this, overall_start_text: str, current_end_text: str) -> PagingResult:
        overall_start: datetime = this.parse_iso_date(overall_start_text)
        current_end: datetime = this.parse_iso_date(current_end_text)

        if current_end < overall_start:
            this.logger.info("No more ranges left to collect")
            return this.create_complete_result()

        current_start: datetime = current_end
        last_good_start: Optional[datetime] = None
        last_good_result: Optional[ApiCallResult] = None

        this.logger.info(
            "Starting next collection window ending at %s",
            this.format_iso_date(current_end)
        )

        while current_start >= overall_start:
            current_result: ApiCallResult = this.test_range(current_start, current_end)

            if this.is_safe_count(current_result.returned_count):
                last_good_start = current_start
                last_good_result = current_result
                current_start = this.get_previous_day(current_start)
                continue

            if this.is_single_day_range(current_start, current_end):
                this.logger.warning(
                    "Single day saturated for %s",
                    this.format_iso_date(current_start)
                )

                return this.create_paging_result(
                    start_date=current_start,
                    end_date=current_end,
                    api_call_result=current_result,
                    is_saturated=True,
                    next_end_date=this.get_previous_day(current_end)
                )

            if last_good_start is None or last_good_result is None:
                raise RuntimeError("No valid non-saturated range was found before overflow.")

            this.logger.info(
                "Returning optimal range %s -> %s",
                this.format_iso_date(last_good_start),
                this.format_iso_date(current_end)
            )

            return this.create_paging_result(
                start_date=last_good_start,
                end_date=current_end,
                api_call_result=last_good_result,
                is_saturated=False,
                next_end_date=last_good_start
            )

        if last_good_start is not None and last_good_result is not None:
            this.logger.info(
                "Returning final optimal range %s -> %s",
                this.format_iso_date(last_good_start),
                this.format_iso_date(current_end)
            )

            return this.create_paging_result(
                start_date=last_good_start,
                end_date=current_end,
                api_call_result=last_good_result,
                is_saturated=False,
                next_end_date=last_good_start
            )

        raise RuntimeError("Unexpected state in collect_next().")
    #--------------------------#