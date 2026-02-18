from src.models.observer import S3EventListener
from typing import List, Set
import weakref
import threading
from concurrent.futures import ThreadPoolExecutor
from src.models.retry_policy import RetryPolicy


class S3EventPublisher:

    def __init__(self):
        # Use WeakSet to avoid memory leaks (holding references to dead listeners)
        self._listeners = weakref.WeakSet()
        # Lock for thread-safe registration/unregistration
        self._lock = threading.Lock()
        # Thread pool for async notifications (non-blocking)
        self._executor = ThreadPoolExecutor(max_workers=5)
        # Retry policy for at-least-once delivery attempts
        self._retry_policy = RetryPolicy()

    def register(self, listener: S3EventListener):
        with self._lock:
            self._listeners.add(listener)

    def unregister(self, listener: S3EventListener):
        with self._lock:
            self._listeners.discard(listener)

    def notify_upload(self, content):
        # Snapshot listeners under lock to avoid "dictionary changed size" iteration error
        with self._lock:
            listeners_snapshot = list(self._listeners)

        # Dispatch notifications asynchronously
        for listener in listeners_snapshot:
            self._executor.submit(self._notify_one, listener, content)

    def _notify_one(self, listener, content):
        """Helper to notify a single listener with error isolation and retries."""
        try:
            # Use retry policy to handle transient failures
            self._retry_policy.execute(listener.on_upload, content)
        except Exception as e:
            # Catch all exceptions to prevent one failure from bringing down the system
            # In a real app, use a proper logger here
            print(f"Failed to notify listener {listener}: {e}")
