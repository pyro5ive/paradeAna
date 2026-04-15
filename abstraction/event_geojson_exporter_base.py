import json
from typing import Any

from abstraction.event_exporter_base import EventExporterBase


class EventGeoJsonExporterBase(EventExporterBase):
    """Provides shared GeoJSON conversion logic for event exporters."""

    def ExtractEventArray(this, responseText: str) -> list[dict[str, Any]]:
        responseJson: dict[str, Any] = json.loads(responseText)
        dataLevel: Any = responseJson.get("data")

        if not isinstance(dataLevel, dict):
            raise ValueError("Response missing data object.")

        grid: Any = dataLevel.get("grid")

        if not isinstance(grid, dict):
            raise ValueError("Response missing data.grid object.")

        eve: Any = grid.get("eve")

        if not isinstance(eve, list):
            raise ValueError("Response missing data.grid.eve array.")

        eventArray: list[dict[str, Any]] = []

        for item in eve:
            if isinstance(item, dict):
                eventArray.append(item)

        return eventArray
    #--------------------------#

    def ConvertEventArrayToFeatureCollection(this, eventArray: list[dict[str, Any]]) -> dict[str, Any]:
        featureArray: list[dict[str, Any]] = []

        for eventRow in eventArray:
            feature: dict[str, Any] | None = this.CreateFeature(eventRow)

            if feature is not None:
                featureArray.append(feature)

        return {
            "type": "FeatureCollection",
            "features": featureArray
        }
    #--------------------------#

    def CreateFeature(this, eventRow: dict[str, Any]) -> dict[str, Any] | None:
        longitude: float | None = this.TryGetFloat(eventRow, "XCoordinate")
        latitude: float | None = this.TryGetFloat(eventRow, "YCoordinate")

        if longitude is None or latitude is None:
            return None

        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            },
            "properties": eventRow
        }
    #--------------------------#

    def TryGetFloat(this, sourceRow: dict[str, Any], key: str) -> float | None:
        value: Any = sourceRow.get(key)

        if value is None:
            return None

        valueText: str = str(value).strip()

        if valueText == "":
            return None

        try:
            return float(valueText)
        except ValueError:
            return None
    #--------------------------#

    def WriteJsonFile(this, filePath: str, content: dict[str, Any]) -> None:
        fileHandle = open(filePath, "w", encoding="utf-8")

        try:
            fileHandle.write(json.dumps(content, indent=2))
        finally:
            fileHandle.close()
    #--------------------------#