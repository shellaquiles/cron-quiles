from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import requests
from ..models import EventNormalized

class BaseAggregator(ABC):
    """Base class for all feed aggregators."""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    @abstractmethod
    def extract(self, source: str | Dict, feed_name: Optional[str] = None) -> List[EventNormalized]:
        """
        Extract events from a source.

        Args:
            source: URL string or dictionary configuration
            feed_name: Optional name of the feed/community

        Returns:
            List of normalized events
        """
        pass
