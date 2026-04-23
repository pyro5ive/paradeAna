import logging
import os
import json
import punq

from abstraction.aggregated_exporter_base import AggregatedExporterBase
from abstraction.api_client_base import ApiClientBase
from abstraction.payload_factory_base import PayloadFactoryBase
from abstraction.paging_coordinator_base import PagingCoordinatorBase
from aggregated_event_geojson_exporter import AggregatedEventGeoJsonExporter
from random_delayed_crime_api_client import RandomDelayedCrimeApiClient
from streaming_event_geo_json_exporter import StreamingEventGeoJsonExporter
from crime_api_client import CrimeApiClient

from date_range_payload_factory import DateRangePayloadFactory
from date_range_paging_proxy import DateRangePagingProxy
from models.paging_result import PagingResult


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

container: punq.Container = punq.Container()

# container.register(logging.Logger, instance=logging.getLogger("jpso"))
container.register(PayloadFactoryBase, DateRangePayloadFactory, payloadFilePath="datasets/community_crime_map/eastBank/payload/request_body_eastBank_all_feat.json")


container.register(
    ApiClientBase,
    RandomDelayedCrimeApiClient,
    url="https://communitycrimemap.com/api/v1/search/load-data",
    bearer_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxOWNhNWM1ZDhlODFkOWM0N2VhYjRiNzI2Njg2NmIzOSIsImF1ZCI6IjNjNzc0YTgxYWM2MTlkMjQzNjFkZWFmNDNjYjFkZDdiIiwic3ViIjoiNDUyYjZhZGIwMjFhZmU5ZTEzNTNlMzVlMmJhODYxOGEiLCJqdGkiOiJEakVSZi9pd0NrZkY5ZmpXaWJLQzgyc01mcG9zeFNiYVJhclpGblBNSUdZb1JWekc4RzdHS0pPSHR3UldodzlTV3J4MXN0b1N3VzA3eU4vaEl2bVZSUT09IiwiaWF0IjoxNzc2NDU2NDczLjc2NzI3MywibmJmIjoxNzc2NDU2NDczLjc2NzI3MywiZXhwIjoxNzc2NDY3MjczLjc2NzI3MywidWlkIjoiWTllQzhiMWljckQrcWZxUVFmeEo1ZDUwejZndHVzZTdxQ29Bd1BTTUFkZ2tocXZlOHRqWkFNZ3JtUzdhZ09US05VL0VGUFJDTHhOS1I1dDFGVXVlL3c9PSJ9.rv1q-dZVFSqYWVWMMMWCleOnptudZJFR0OuCku-BSxE",
    timeout_seconds=120
)

container.register( PagingCoordinatorBase,    DateRangePagingProxy);
paging_proxy: PagingCoordinatorBase = container.resolve(PagingCoordinatorBase)
exporter: AggregatedExporterBase = StreamingEventGeoJsonExporter(outputRootPath="datasets/community_crime_map/eastbank/events", fileName="2019_2016_everyday_eastbank.geojson")

dateRanges: list[dict[str, str]] = [
     # {"start": "2026-01-01", "end": "2026-04-20"},
     #  {"start": "2025-01-01", "end": "2025-12-31"},
     #   {"start": "2024-01-01", "end": "2024-12-31"},
    #  {"start": "2023-01-01", "end": "2023-12-31"},
    #  {"start": "2022-01-01", "end": "2022-12-31"},
    # {"start": "2021-01-01", "end": "2021-12-31"},
    # {"start": "2020-01-01", "end": "2020-10-31"},
     {"start": "2019-01-01", "end": "2019-12-31"},
     {"start": "2018-01-01", "end": "2018-12-31"},
     {"start": "2017-01-01", "end": "2017-12-31"},
     {"start": "2016-01-01", "end": "2016-12-31"},
    # {"start": "2015-01-01", "end": "2015-12-31"},
    # {"start": "2014-01-01", "end": "2014-12-31"}
]

# dateRanges: list[dict[str, str]] = [    {"start": "2025-04-15", "end": "2025-04-19"}, ]


for dateRange in dateRanges:
    overall_start_text: str = dateRange["start"]
    current_end_text: str = dateRange["end"]

    while True:
        result: PagingResult = paging_proxy.collect_next(overall_start_text, current_end_text)

        print(result.requested_start, result.requested_end, result.returned_count, result.is_saturated)

        if result.is_complete and result.returned_count == 0:
            break

        filePath: str = exporter.ExportResult(result.requested_start, result.response_text)

        print(filePath)

        if result.is_complete:
            break

        if result.next_end_date is None:
            break

        current_end_text = result.next_end_date

filePath: str = exporter.Finalize()

print(filePath)