import os
from datetime import datetime

from abstraction.event_geojson_exporter_base import EventGeoJsonExporterBase


class PagedEventGeoJsonExporter(EventGeoJsonExporterBase):
    """Writes one GeoJSON file per response into output/<run timestamp>/<year>/ files."""

    def __init__(this, outputRootPath: str = "output") -> None:
        this.outputRootPath = outputRootPath
        this.executionTimestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        this.runFolderPath = os.path.join(this.outputRootPath, this.executionTimestamp)
        this.fileIndex = 1

        os.makedirs(this.runFolderPath, exist_ok=True)
    #--------------------------#

    def ExportResult(this, requestDateText: str, responseText: str) -> str:
        eventArray: list[dict[str, object]] = this.ExtractEventArray(responseText)
        featureCollection: dict[str, object] = this.ConvertEventArrayToFeatureCollection(eventArray)
        filePath: str = this.BuildFilePath(requestDateText)

        this.WriteJsonFile(filePath, featureCollection)

        this.fileIndex += 1

        return filePath
    #--------------------------#

    def BuildFilePath(this, requestDateText: str) -> str:
        yearFolderPath: str = this.GetYearFolderPath(requestDateText)
        fileName: str = "page_" + str(this.fileIndex).zfill(4) + "_" + requestDateText + ".geojson"

        return os.path.join(yearFolderPath, fileName)
    #--------------------------#

    def GetYearFolderPath(this, requestDateText: str) -> str:
        yearText: str = requestDateText[0:4]
        yearFolderPath: str = os.path.join(this.runFolderPath, yearText)

        os.makedirs(yearFolderPath, exist_ok=True)

        return yearFolderPath
    #--------------------------#