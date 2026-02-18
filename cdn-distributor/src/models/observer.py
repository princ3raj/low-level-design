from abc import ABC, abstractmethod
from typing import Any


class S3EventListener(ABC):

    @abstractmethod
    def on_upload(self, content):
        pass


class EdgeEventListener(ABC):

    @abstractmethod
    def push(self, content: Any):
        pass
