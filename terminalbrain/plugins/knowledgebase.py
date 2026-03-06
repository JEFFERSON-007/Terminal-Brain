"""Optional knowledge base module for Terminal Brain.

Provides local knowledge base with semantic search.
Install with: terminal-brain install knowledgebase

"""


def init():
    """Initialize knowledge base module."""
    return {
        "name": "knowledgebase",
        "features": ["semantic_search", "rag"],
        "description": "Local knowledge base with vector search",
    }


class KnowledgeBase:
    """Local knowledge base with semantic search."""
    
    def __init__(self):
        self.index = None
        self.embeddings = None
    
    def build_index(self, documents: list) -> None:
        """Build FAISS index from documents."""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            
            # Generate embeddings
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(documents)
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)
            self.embeddings = embeddings
            
        except ImportError as e:
            raise RuntimeError(f"Required packages not installed. Run: terminal-brain install knowledgebase. Error: {e}")
    
    def search(self, query: str, top_k: int = 5) -> list:
        """Search knowledge base."""
        if not self.index:
            raise RuntimeError("Knowledge base not initialized")
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = model.encode([query])
            
            distances, indices = self.index.search(query_embedding, top_k)
            return indices[0].tolist()
        except Exception as e:
            raise RuntimeError(f"Search failed: {e}")
