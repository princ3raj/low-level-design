import hashlib
from typing import List, Optional
from uuid import uuid4

class Content:
    def __init__(self, name: str, size: int, data: str, region_tags: Optional[List[str]] = None):
        self._id = str(uuid4())
        self.name = name
        self.file_size = size
        self.data = data
        self.region_tags = region_tags or []
        self.checksum = self._calculate_checksum()

    @property
    def id(self):
        return self._id

    def _calculate_checksum(self) -> str:
        """Calculates MD5 checksum of the content data."""
        return hashlib.md5(self.data.encode('utf-8')).hexdigest()

    def __str__(self):
        return f"{self.name} (Size: {self.file_size}, Checksum: {self.checksum[:8]})"

    @property
    def file_type(self):
        return self._file_type
