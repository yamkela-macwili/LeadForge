from abc import ABC, abstractmethod

class BaseEnricher(ABC):
    @abstractmethod
    def enrich(self, lead_data: dict) -> dict:
        """
        Enriches a single lead dictionary with additional data.
        Returns the enriched dictionary.
        """
        pass
