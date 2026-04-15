import logging
import os
import json
import punq

from abstraction.aggregated_exporter_base import AggregatedExporterBase
from abstraction.api_client_base import ApiClientBase
from abstraction.payload_factory_base import PayloadFactoryBase
from abstraction.paging_coordinator_base import PagingCoordinatorBase
from aggregated_event_geojson_exporter import AggregatedEventGeoJsonExporter
from crime_api_client import CrimeApiClient
from delayed_crime_api_client import DelayedCrimeApiClient
from date_range_payload_factory import DateRangePayloadFactory
from date_range_paging_proxy import DateRangePagingProxy
from models.paging_result import PagingResult


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

container: punq.Container = punq.Container()

# container.register(logging.Logger, instance=logging.getLogger("jpso"))
container.register(PayloadFactoryBase, DateRangePayloadFactory, payloadFilePath="payloads/jpso/request_body.json")

# container.register(
#     ApiClientBase,
#     CrimeApiClient,
#     url="https://communitycrimemap.com/api/v1/search/load-data",
#     bearer_token=" eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxOWNhNWM1ZDhlODFkOWM0N2VhYjRiNzI2Njg2NmIzOSIsImF1ZCI6IjNjNzc0YTgxYWM2MTlkMjQzNjFkZWFmNDNjYjFkZDdiIiwic3ViIjoiNzdmNzgzZmQ3MWEzMmNlNmQ2YWNiZTRlZmUzY2U0ZGEiLCJqdGkiOiJZOTVyc2NKZ3c3MmxrZys2NXpWWkg2cDVYZzJXNWNUYk0vU2ZjbW9Wa2k3QjNXRnJNd29xekRtRnBRcHhHZzEvNUVkU2RRTk5uYmQwVEc0NVhPc3BQZz09IiwiaWF0IjoxNzc2MjE2Nzk2Ljk2OTU3MiwibmJmIjoxNzc2MjE2Nzk2Ljk2OTU3MiwiZXhwIjoxNzc2MjI3NTk2Ljk2OTU3MiwidWlkIjoidVlCWTAydWZPd1hJTkdoME1TWEVkK1BhNlZYbi9aL3lTMnUwU29icytmNFhMZS9hNStFb2ZnN21GL2tuMXI5empxSHNkOEV6VUZJT05tZHlidFlrVGc9PSJ9.wdTzowFm3gX6DHbbrLeikZBGR2hUouffZp5qyjutY0w",
#     timeout_seconds=120
# )
container.register(
    ApiClientBase,
    DelayedCrimeApiClient,
    url="https://communitycrimemap.com/api/v1/search/load-data",
    bearer_token=" eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxOWNhNWM1ZDhlODFkOWM0N2VhYjRiNzI2Njg2NmIzOSIsImF1ZCI6IjNjNzc0YTgxYWM2MTlkMjQzNjFkZWFmNDNjYjFkZDdiIiwic3ViIjoiNzdmNzgzZmQ3MWEzMmNlNmQ2YWNiZTRlZmUzY2U0ZGEiLCJqdGkiOiJZOTVyc2NKZ3c3MmxrZys2NXpWWkg2cDVYZzJXNWNUYk0vU2ZjbW9Wa2k3QjNXRnJNd29xekRtRnBRcHhHZzEvNUVkU2RRTk5uYmQwVEc0NVhPc3BQZz09IiwiaWF0IjoxNzc2MjE2Nzk2Ljk2OTU3MiwibmJmIjoxNzc2MjE2Nzk2Ljk2OTU3MiwiZXhwIjoxNzc2MjI3NTk2Ljk2OTU3MiwidWlkIjoidVlCWTAydWZPd1hJTkdoME1TWEVkK1BhNlZYbi9aL3lTMnUwU29icytmNFhMZS9hNStFb2ZnN21GL2tuMXI5empxSHNkOEV6VUZJT05tZHlidFlrVGc9PSJ9.wdTzowFm3gX6DHbbrLeikZBGR2hUouffZp5qyjutY0w",
    timeout_seconds=120,
    delay_seconds=3.0
)

container.register(
    PagingCoordinatorBase,
    DateRangePagingProxy
)

paging_proxy: PagingCoordinatorBase = container.resolve(PagingCoordinatorBase)
exporter: AggregatedExporterBase = AggregatedEventGeoJsonExporter("output")

# dateRanges: list[dict[str, str]] = [
#     {"start": "2016-01-26", "end": "2016-02-09"},
#     {"start": "2017-02-14", "end": "2017-02-28"},
#     {"start": "2018-01-30", "end": "2018-02-13"},
#     {"start": "2019-02-19", "end": "2019-03-05"},
#     {"start": "2020-02-11", "end": "2020-02-25"},
#     {"start": "2021-02-02", "end": "2021-02-16"},
#     {"start": "2022-02-15", "end": "2022-03-01"},
#     {"start": "2023-02-07", "end": "2023-02-21"},
#     {"start": "2024-01-30", "end": "2024-02-13"},
#     {"start": "2025-02-18", "end": "2025-03-04"},
#     {"start": "2026-02-03", "end": "2026-02-17"}
# ]


dateRanges: list[dict[str, str]] = [
    {"start": "2026-01-01", "end": "2026-04-01"},
    {"start": "2025-01-01", "end": "2025-04-01"},
    {"start": "2024-01-01", "end": "2024-04-01"},
    {"start": "2023-01-01", "end": "2023-04-01"},
    {"start": "2022-01-01", "end": "2022-04-01"},
    {"start": "2021-01-01", "end": "2021-04-01"},
    {"start": "2020-01-01", "end": "2020-04-01"},
    {"start": "2019-01-01", "end": "2019-04-01"},
    {"start": "2018-01-01", "end": "2018-04-01"},
    {"start": "2017-01-01", "end": "2017-04-01"},
    {"start": "2016-01-01", "end": "2016-04-01"}
]


for dateRange in dateRanges:
    overall_start_text: str = dateRange["start"]
    current_end_text: str = dateRange["end"]

    while True:
        result: PagingResult = paging_proxy.collect_next(overall_start_text, current_end_text)

        if result.is_complete:
            break

        print(result.requested_start, result.requested_end, result.returned_count, result.is_saturated)

        filePath: str = exporter.ExportResult(result.requested_start, result.response_text)

        print(filePath)

        if result.next_end_date is None:
            break

        current_end_text = result.next_end_date

filePath: str = exporter.Finalize()

print(filePath)