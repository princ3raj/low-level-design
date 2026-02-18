from src.models.content import Content
from src.models.observer import S3EventListener, EdgeEventListener
from src.models.retry_policy import RetryPolicy
from typing import List, Dict
from time import sleep


class CDNController(S3EventListener):

    def __init__(self, retry_policy: RetryPolicy):
        self._edge_nodes: List[EdgeEventListener] = []
        self._retry_policy = retry_policy
        self._processed_checksums: Set[str] = set()
        self._latest_versions: Dict[str, str] = {} # name -> checksum
        self._content_store: Dict[str, Content] = {} # name -> Content object (Origin Storage)

    def register_edge_node(self, edge_node: EdgeEventListener):
        self._edge_nodes.append(edge_node)

    def unregister_edge_node(self, edge_node: EdgeEventListener):
        self._edge_nodes.remove(edge_node)

    def fetch_content(self, name: str) -> Optional[Content]:
        """Acts as the 'Origin' for Edge Pull Fallback."""
        if name in self._content_store:
            print(f"Origin: Serving {name} to edge node.")
            return self._content_store[name]
        print(f"Origin: 404 Not Found for {name}")
        return None

    def on_upload(self, content: Content):
        print(f"CDN received new content notification: {content.name}")
        
        # Store in Origin (Simulating S3/Origin Shield)
        self._content_store[content.name] = content
        
        # 1. Checksum Deduplication
        if content.checksum in self._processed_checksums:
            print(f"Skipping duplicate content {content.name} (Checksum: {content.checksum[:8]})")
            return
        
        # 3. Delta Update Simulation
        if content.name in self._latest_versions:
             print(f"File {content.name} has changed. Calculating Delta... (Simulated)")
             print(f"Sending Delta Update for {content.name}...")
        
        self._processed_checksums.add(content.checksum)
        self._latest_versions[content.name] = content.checksum
        
        self._push_to_edges(content)

    def _push_to_edges(self, content: Content):
        for node in self._edge_nodes:
            # 2. Region-Aware Routing
            # If content has region tags, only push to nodes in those regions
            if content.region_tags and node.region not in content.region_tags:
                print(f"Skipping {node} (Region: {node.region}) for {content.name} (Tags: {content.region_tags})")
                continue

            print(f"Pushing {content.name} to {node}...")
            self._retry_policy.execute(node.push, content)

    def invalidate_content(self, content: Content):
        """Simulates Invalidation (Pull Model)"""
        print(f"Invalidating {content.name} across CDN...")
        for node in self._edge_nodes:
             # Invalidation is usually global, or can be regionally scoped too
             self._retry_policy.execute(node.invalidate, content.name)


class MumbaiEdgeNode(EdgeEventListener):
    def __init__(self, origin=None):
        super().__init__(origin)

    @property
    def region(self):
        return "IN"

    def push(self, content: Content):
        sleep(0.5)
        self._cache[content.name] = content
        print(f"{content.name} successfully pushed/cached at {self}")
    
    def invalidate(self, content_id: str):
        if content_id in self._cache:
            print(f"{self}: Marking {content_id} as STALE. (Will fetch new version on next request)")
            # In a real system, we might delete it or set a 'stale' flag
            del self._cache[content_id]
        else:
            print(f"{self}: {content_id} not in cache, nothing to invalidate.")

    def __str__(self):
        return "Mumbai 123 Edge Node"


class CaliforniaEdgeNode(EdgeEventListener):
    def __init__(self, origin=None):
        super().__init__(origin)

    @property
    def region(self):
        return "US"

    def push(self, content: Content):
        sleep(0.5)
        self._cache[content.name] = content
        print(f"{content.name} successfully pushed/cached at {self}")
    
    def invalidate(self, content_id: str):
        if content_id in self._cache:
             print(f"{self}: Marking {content_id} as STALE.")
             del self._cache[content_id]

    def __str__(self):
        return "California 69 Edge Node"