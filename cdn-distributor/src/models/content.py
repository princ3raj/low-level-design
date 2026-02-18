from uuid import uuid4
from random import randint


class Content:

    def __init__(self, name, description, file_type):
        self._id = str(uuid4())
        self._name = name
        self._description = description
        self._file_type = file_type
        self._file_size = f"{randint(100,500)} KB"

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def file_size(self):
        return self._file_size

    @property
    def file_type(self):
        return self._file_type
