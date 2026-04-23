import json
import os
from datetime import datetime
from typing import Any, TextIO

from abstraction.aggregated_exporter_base import AggregatedExporterBase


class StreamingEventGeoJsonExporter(AggregatedExporterBase):
    """Writes GeoJSON features incrementally into a single FeatureCollection file."""

    def __init__(this, outputRootPath: str = "output", fileName: str = "events.geojson") -> None:
        this.outputRootPath = outputRootPath
        this.fileName = fileName
        this.executionTimestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        this.runFolderPath = os.path.join(this.outputRootPath, this.executionTimestamp)
        this.filePath = os.path.join(this.runFolderPath, this.fileName)
        this.fileHandle: TextIO | None = None
        this.hasWrittenAnyFeature = False
        this.isFinalized = False

        os.makedirs(this.runFolderPath, exist_ok=True)
    #--------------------------#

    def ExportResult(this, requestDateText: str, responseText: str) -> str:
        if this.isFinalized:
            raise RuntimeError("Exporter has already been finalized.")

        this.EnsureFileInitialized()

        eventArray: list[dict[str, Any]] = this.ExtractEventArray(responseText)

        for eventRow in eventArray:
            feature: dict[str, Any] | None = this.CreateFeature(eventRow)

            if feature is not None:
                this.WriteFeature(feature)

        this.FlushToDisk()

        return this.filePath
    #--------------------------#

    def Finalize(this) -> str:
        if this.isFinalized:
            return this.filePath

        this.EnsureFileInitialized()

        if this.fileHandle is None:
            raise RuntimeError("GeoJSON file handle was not initialized.")

        this.fileHandle.write("]}")
        this.FlushToDisk()
        this.fileHandle.close()
        this.fileHandle = None
        this.isFinalized = True

        return this.filePath
    #--------------------------#

    def EnsureFileInitialized(this) -> None:
        if this.fileHandle is not None:
            return

        this.fileHandle = open(this.filePath, "w", encoding="utf-8")
        this.fileHandle.write('{"type":"FeatureCollection","features":[')
        this.FlushToDisk()
    #--------------------------#

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

    def WriteFeature(this, feature: dict[str, Any]) -> None:
        if this.fileHandle is None:
            raise RuntimeError("GeoJSON file handle was not initialized.")

        if this.hasWrittenAnyFeature:
            this.fileHandle.write(",")

        this.fileHandle.write(json.dumps(feature))
        this.hasWrittenAnyFeature = True
    #--------------------------#

    def FlushToDisk(this) -> None:
        if this.fileHandle is None:
            raise RuntimeError("GeoJSON file handle was not initialized.")

        this.fileHandle.flush()
        os.fsync(this.fileHandle.fileno())
    #--------------------------#