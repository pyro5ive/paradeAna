import abc


class AggregatedExporterBase(abc.ABC):
    """Defines the contract for exporters that aggregate multiple responses into one artifact."""

    @abc.abstractmethod
    def ExportResult(this, requestDateText: str, responseText: str) -> str:
        """Aggregates one response payload and returns the output file path."""
        raise NotImplementedError()
    #--------------------------#

    @abc.abstractmethod
    def Finalize(this) -> str:
        """Writes the final aggregated artifact and returns the output file path."""
        raise NotImplementedError()
    #--------------------------#