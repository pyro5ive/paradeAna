import logging
import punq

from abstraction.api_client_base import ApiClientBase
from abstraction.payload_factory_base import PayloadFactoryBase
from abstraction.paging_coordinator_base import PagingCoordinatorBase
from crime_api_client import CrimeApiClient
from date_range_payload_factory import DateRangePayloadFactory
from date_range_paging_proxy import DateRangePagingProxy
from models.paging_result import PagingResult
from payloads.jpso  import base_payload
from payloads.location_payload import location_payload
from payloads.type_selection_payload import type_selection_payload


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

container: punq.Container = punq.Container()

container.register(logging.Logger, instance=logging.getLogger("jpso"))

container.register(PayloadFactoryBase, DateRangePayloadFactory, base_payload=base_payload, location_payload=location_payload, type_selection_payload=type_selection_payload, logger=container.resolve(logging.Logger))
container.register(ApiClientBase,
                   CrimeApiClient,
                   url="https://communitycrimemap.com/api/v1/search/load-data",
                   bearer_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxOWNhNWM1ZDhlODFkOWM0N2VhYjRiNzI2Njg2NmIzOSIsImF1ZCI6IjNjNzc0YTgxYWM2MTlkMjQzNjFkZWFmNDNjYjFkZDdiIiwic3ViIjoiODQzMmIzODU2MDNlMGNkYWQwYmRiNjgxMzA3YmMzMWMiLCJqdGkiOiJHYXhCOW95ZTVENUdpeFRqNFVRZnY3SlRGNVZVWmpheElFK255aDNOU3pnR0N4QTlkdGxuRGVCSHpqVUVyYkxzYzlKeDdwOVB4MnF3dmtWVWtaU2s1dz09IiwiaWF0IjoxNzc2MjA1NzE1LjY1NjA1NCwibmJmIjoxNzc2MjA1NzE1LjY1NjA1NCwiZXhwIjoxNzc2MjE2NTE1LjY1NjA1NCwidWlkIjoiRmxhOEF3cG9kV3NuQys0YkVSa0RISWxKMzJuWGpPRWZxSHdXdkUzTFdhalVKc0tGWXNKUElyVGExQXNkWkNHQXVLTXM4ZGNLWFlCWUlJck1DcHNNTlE9PSJ9.7t-F1JgPcGKQ5i42FZG91hVLHNBTGn0Twld2rZ5MGrk",
                   timeout_seconds=120,
                   logger=container.resolve(logging.Logger))
container.register(PagingCoordinatorBase, DateRangePagingProxy, payload_factory=container.resolve(PayloadFactoryBase), api_client=container.resolve(ApiClientBase), row_cap=500, logger=container.resolve(logging.Logger))

paging_proxy: PagingCoordinatorBase = container.resolve(PagingCoordinatorBase)

overall_start_text: str = "2026-01-03"
current_end_text: str = "2026-02-01"

while True:
    result: PagingResult = paging_proxy.collect_next(overall_start_text, current_end_text)

    if result.is_complete:
        break

    print(result.requested_start, result.requested_end, result.returned_count, result.is_saturated)

    # save result.response_text or result.payload here

    if result.next_end_date is None:
        break

    current_end_text = result.next_end_date
#--------------------------#