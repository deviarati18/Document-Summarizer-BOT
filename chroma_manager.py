import chromadb
import os

class ChromaDBManager:
    def __init__(self, db_path="./chroma_db"):
        """Initialize ChromaDB client and collection."""
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection("document_summaries")

    def add_summary(self, doc_id, summary):
        """Add document summary to ChromaDB."""
        self.collection.add(
            ids=[doc_id],
            metadatas=[{"file_name": doc_id}],
            documents=[summary]
        )

    def search(self, query, top_n=5):
        """Query the knowledge base."""
        results = self.collection.query(query_texts=[query], n_results=top_n)
        return results.get("documents", [[]])[0] if results else []

# Usage Example:
if __name__ == "__main__":
    db = ChromaDBManager()
    print(db.search("AI research"))
