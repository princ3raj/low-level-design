from src.models.observer import S3EventListener
from typing import List


class S3EventPublisher:

    def __init__(self):
        self._listeners: List[S3EventListener] = []

    def register(self, listener: S3EventListener):
        self._listeners.append(listener)

    def unregister(self, listener: S3EventListener):
        self._listeners.remove(listener)

    def notify_upload(self, content):
        for listener in self._listeners:
            listener.on_upload(content)
