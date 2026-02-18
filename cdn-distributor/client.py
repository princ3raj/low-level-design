from src.models.content import Content
from src.models.retry_policy import RetryPolicy
from src.s3.upload import S3Bucket
from src.s3.publisher import S3EventPublisher
from src.cdn.controller import CDNController, MumbaiEdgeNode, CaliforniaEdgeNode


class Client:

    def __init__(self, name, bucket: S3Bucket):
        self._name = name
        self._bucket = bucket

    @property
    def name(self):
        return self._name

    def upload(self, content: Content):
        self._bucket.upload(content=content)


if __name__ == "__main__":
    # 1. Initialize S3 Event Publisher
    publisher = S3EventPublisher()

    # 2. Initialize S3 Bucket with publisher
    bucket = S3Bucket(publisher=publisher)

    # 3. Initialize Retry Policy
    retry_policy = RetryPolicy(max_retries=3, delay=0.2)

    # 4. Initialize CDN Controller with retry policy
    cdn = CDNController(retry_policy=retry_policy)

    # 5. Initialize Edge Nodes
    mumbai = MumbaiEdgeNode()
    california = CaliforniaEdgeNode()

    # 6. Wire up the Observer Pattern
    cdn.register_edge_node(mumbai)
    cdn.register_edge_node(california)
    publisher.register(cdn)

    # 7. Client uploads content
    content = Content(
        name="PRODUCTION_ASSET_01.MP4", 
        description="High-quality video asset", 
        file_type="MP4"
    )
    client = Client(name="Prince", bucket=bucket)
    client.upload(content=content)
