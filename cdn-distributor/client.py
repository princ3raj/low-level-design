from src.models.content import Content
from src.models.retry_policy import RetryPolicy
import time
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
    
    # SYSTEM SETUP
    # 1. Create the S3 Publisher (The "Broadcaster")
    s3_publisher = S3EventPublisher()
    
    # 2. Create the CDN Controller (The "Smart Router")
    #    It has a RetryPolicy (3 retries, 1s delay) to handle network blips
    retry_policy = RetryPolicy(max_retries=3, delay=1.0)
    cdn_controller = CDNController(retry_policy)
    
    # 3. Connect them: S3 -> CDN
    s3_publisher.register(cdn_controller)
    
    # 4. Create the S3 Bucket (The "Source")
    bucket = S3Bucket(s3_publisher)
    
    # 5. Add Edge Nodes (The "Receivers")
    mumbai_node = MumbaiEdgeNode(origin=cdn_controller)    # Region: IN
    cali_node = CaliforniaEdgeNode(origin=cdn_controller)  # Region: US
    
    cdn_controller.register_edge_node(mumbai_node)
    cdn_controller.register_edge_node(cali_node)
    
    print("\n--- 1. Standard Upload (Both Regions) ---")
    # SIMULATE USER UPLOAD
    video = Content(
        name="movie.mp4",
        size=1024,
        data="video_data_bits",
        region_tags=["IN", "US"] # Tagged for both
    )
    bucket.upload(video)

    print("\n--- 2. Region-Specific Upload (US Only) ---")
    us_content = Content(
        name="superbowl.mov",
        size=500,
        data="us_exclusive_data",
        region_tags=["US"]
    )
    bucket.upload(us_content)

    print("\n--- 3. Deduplication Test ---")
    # Uploading the exact same video again
    bucket.upload(video)
    
    # Wait for async tasks to finish
    time.sleep(2)

    print("\n--- 4. Invalidation Test ---")
    # Mark content as stale
    cdn_controller.invalidate_content(video)

    print("\n--- 5. Edge Pull Fallback Test ---")
    # Scenario: Mumbai node lost its data (simulated crash/restart)
    # But the content is still safely stored in the Origin (CDNController)
    print(f"Simulating data loss on {mumbai_node}...")
    mumbai_node._cache = {} # Wipe cache
    
    # User requests content from Mumbai node
    print(f"User requests {video.name} from {mumbai_node}...")
    pulled_content = mumbai_node.get_content(video.name)
    
    if pulled_content:
        print(f"SUCCESS: User got content! (Served via Origin Pull)")
    else:
        print("FAIL: User got 404.")
