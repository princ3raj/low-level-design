from abc import ABC, abstractmethod
from typing import Any


class S3EventListener(ABC):

    @abstractmethod
    def on_upload(self, content):
        pass


class EdgeEventListener(ABC):

    def __init__(self, origin=None):
        self._origin = origin
        self._cache = {}

    @property
    @abstractmethod
    def region(self) -> str:
        """Returns the region code (e.g., 'US', 'IN') of this edge node."""
        pass

    def get_content(self, name: str):
        """Tries to get content from cache, falls back to Origin Pull."""
        if name in self._cache:
            print(f"HIT: {name} served from {self} cache.")
            return self._cache[name]
        
        print(f"MISS: {name} not found at {self}. Pulling from Origin...")
        if self._origin:
            content = self._origin.fetch_content(name)
            if content:
                self._cache[name] = content
                print(f"Origin Pull Successful: cached {name} at {self}")
                return content
        
        raise Exception(f"404 Not Found: {name}")

    @abstractmethod
    def push(self, content: Any):
        """Pushes full content to the edge node."""
        pass

    @abstractmethod
    def invalidate(self, content_id: str):
        """Signals the edge node to mark content as stale (pull model)."""
        pass
