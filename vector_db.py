import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class QdrantStorage:
    def __init__(self, collection="docs", dim=3072):
        # 1. Pull environment variables (configured in your Cloud deployment dashboard)
        qdrant_url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        # 2. Fall back to localhost only if cloud environment variables aren't set
        if not qdrant_url:
            qdrant_url = "http://localhost:6333"
            print("⚠️ QDRANT_URL env var not found. Falling back to local: http://localhost:6333")
        else:
            print(f"🚀 Connecting securely to Qdrant Cloud Cluster at: {qdrant_url}")

        # 3. Initialize the client safely with or without an API Key
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=api_key,  # Will pass None cleanly if running locally
            timeout=30
        )
        self.collection = collection
        
        # 4. Auto-verify or create collection securely on initialization
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) 
            for i in range(len(ids))
        ]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5):
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            with_payload=True,
            limit=top_k
        )
        contexts = []
        sources = set()

        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text:
                contexts.append(text)
                sources.add(source)

        return {"contexts": contexts, "sources": list(sources)}
