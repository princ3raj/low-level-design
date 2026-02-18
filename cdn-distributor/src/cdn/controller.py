from src.models.content import Content
from src.models.observer import S3EventListener, EdgeEventListener
from src.models.retry_policy import RetryPolicy
from typing import List, Dict
from time import sleep


class CDNController(S3EventListener):

    def __init__(self, retry_policy: RetryPolicy):
        self._edge_nodes: List[EdgeEventListener] = []
        self._retry_policy = retry_policy

    def register_edge_node(self, edge_node: EdgeEventListener):
        self._edge_nodes.append(edge_node)

    def unregister_edge_node(self, edge_node: EdgeEventListener):
        self._edge_nodes.remove(edge_node)

    def on_upload(self, content: Content):
        print(f"CDN received new content notification: {content.name}")
        self._push_to_edges(content)

    def _push_to_edges(self, content: Content):
        for node in self._edge_nodes:
            print(f"Pushing {content.name} to {node}...")
            self._retry_policy.execute(node.push, content)


class MumbaiEdgeNode(EdgeEventListener):
    def __init__(self):
        self._cache: Dict[str, Content] = {}

    def push(self, content: Content):
        sleep(0.5)
        self._cache[content.name] = content
        print(f"{content.name} successfully cached at {self}")
    
    def __str__(self):
        return "Mumbai 123 Edge Node"


class CaliforniaEdgeNode(EdgeEventListener):
    def __init__(self):
        self._cache: Dict[str, Content] = {}

    def push(self, content: Content):
        sleep(0.5)
        self._cache[content.name] = content
        print(f"{content.name} successfully cached at {self}")
    
    def __str__(self):
        return "California 69 Edge Node"