import logging
from datetime import datetime
from datetime import timedelta

from abstraction.api_client_base import ApiClientBase
from abstraction.paging_coordinator_base import PagingCoordinatorBase
from abstraction.payload_factory_base import PayloadFactoryBase
from models.api_call_result import ApiCallResult
from models.paging_result import PagingResult


class DateRangePagingProxy(PagingCoordinatorBase):
    """Requests one day at a time and moves backward by day."""

    def __init__(
        this,
        payload_factory: PayloadFactoryBase,
        api_client: ApiClientBase
    ) -> None:
        this.payload_factory = payload_factory
        this.api_client = api_client
        this.logger = logging.getLogger(__name__ + ".DateRangePagingProxy")
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

    def create_paging_result(
        this,
        request_date: datetime,
        api_call_result: ApiCallResult
    ) -> PagingResult:
        next_end_date: str = this.format_iso_date(this.get_previous_day(request_date))

        return PagingResult(
            requested_start=this.format_iso_date(request_date),
            requested_end=this.format_iso_date(request_date),
            returned_count=api_call_result.returned_count,
            is_saturated=False,
            payload=api_call_result.payload,
            response_text=api_call_result.response_text,
            next_end_date=next_end_date,
            is_complete=False
        )
    #--------------------------#

    def request_day(this, request_date: datetime) -> ApiCallResult:
        payload: dict = this.payload_factory.build_payload(request_date, request_date)

        this.logger.info(
            "Requesting range %s -> %s",
            this.format_iso_date(request_date),
            this.format_iso_date(request_date)
        )

        return this.api_client.execute(payload)
    #--------------------------#

    def collect_next(this, overall_start_text: str, current_end_text: str) -> PagingResult:
        overall_start: datetime = this.parse_iso_date(overall_start_text)
        current_end: datetime = this.parse_iso_date(current_end_text)

        if current_end < overall_start:
            this.logger.info("No more ranges left to collect")
            return this.create_complete_result()

        return this.create_paging_result(
            request_date=current_end,
            api_call_result=this.request_day(current_end)
        )
    #--------------------------#