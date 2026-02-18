from src.models.content import Content
from src.s3.publisher import S3EventPublisher
from uuid import uuid4
from time import sleep


class S3Bucket:

    def __init__(self, publisher: S3EventPublisher):
        self._token = uuid4()
        self._publisher = publisher

    def upload(self, content: Content):
        print(f"Uploading {content.name} of size {content.file_size} to S3.......")
        sleep(0.5)
        print(f"{content.name} Uploaded Successfully to S3.....")
        self._publisher.notify_upload(content)
