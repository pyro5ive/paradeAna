import abc


class EventExporterBase(abc.ABC):
    """Defines the contract for exporting event responses."""

    @abc.abstractmethod
    def ExportResult(this, requestDateText: str, responseText: str) -> str:
        """Exports one response payload and returns the output file path."""
        raise NotImplementedError()
    #--------------------------#