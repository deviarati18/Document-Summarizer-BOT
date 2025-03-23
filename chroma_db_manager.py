
# 🚀 AI-Powered Document Summarizer
# Created by Devi C. Arati (@deviarati18) | GitHub: https://github.com/deviarati18


import chromadb
import os
import streamlit as st  # For better error display in Streamlit apps

class ChromaDBManager:
    def __init__(self, db_path="./chroma_db"):
        """Initialize ChromaDB persistent client and collection."""
        os.makedirs(db_path, exist_ok=True)  # Ensure directory exists

        # Initialize ChromaDB Client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or retrieve collection
        self.collection = self.client.get_or_create_collection("document_summaries")

    def list_documents(self):
        """List stored document names."""
        try:
            stored_docs = self.collection.get(include=["metadatas"])
            metadatas = stored_docs.get("metadatas", [])
            return [doc.get("filename", "Unknown") for doc in metadatas if isinstance(doc, dict)]
        except Exception as e:
            st.error(f"⚠️ Error listing documents: {e}")
            return []  # Return empty list instead of None

    def is_document_stored(self, document_name):
        """Check if a document already exists in the database."""
        return document_name in self.list_documents()

    def add_summary(self, doc_name, summary):
        """Add or update a document summary in ChromaDB."""
        try:
            if self.is_document_stored(doc_name):
                self.collection.delete(ids=[doc_name])  # Delete existing document before re-adding

            self.collection.add(
                ids=[doc_name], 
                documents=[summary], 
                metadatas=[{"filename": doc_name}]
            )
            return f"✅ Summary for '{doc_name}' stored successfully."
        except Exception as e:
            st.error(f"⚠️ Error adding/updating summary for {doc_name}: {e}")
            return "❌ Failed to store summary."

    def get_summary(self, doc_name):
        """Retrieve the summary of a document."""
        try:
            results = self.collection.get(ids=[doc_name])
            if results and results.get("documents") and isinstance(results["documents"], list):
                return results["documents"][0] if results["documents"] else ""
        except Exception as e:
            st.error(f"❌ Error retrieving summary for {doc_name}: {e}")
        return ""  # Return empty string instead of None

    def delete_document(self, document_name):
        """Deletes a document from the ChromaDB collection."""
        try:
            self.collection.delete(ids=[document_name])
            return f"✅ Document '{document_name}' deleted successfully."
        except Exception as e:
            st.error(f"⚠️ Error deleting document {document_name}: {e}")
            return "❌ Failed to delete document."

    def clear_knowledgebase(self):
        """Clear all documents from the knowledge base."""
        try:
            self.client.delete_collection("document_summaries")
            self.collection = self.client.get_or_create_collection("document_summaries")  # Recreate collection
            return "✅ Knowledge base cleared successfully."
        except Exception as e:
            st.error(f"⚠️ Error clearing knowledge base: {e}")
            return "❌ Failed to clear knowledge base."

    def search(self, query, n_results=3):
        """Search the knowledge base and return relevant document summaries."""
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)

            if results and "documents" in results and isinstance(results["documents"], list):
                return {"documents": results["documents"][:n_results]}  # Ensure correct return format
        except Exception as e:
            st.error(f"⚠️ Error during search: {e}")
        return {"documents": []}  # Return empty structure to avoid errors

# Debugging: Check stored data
if __name__ == "__main__":
    db = ChromaDBManager()
    print("📚 Current Knowledge Base:", db.list_documents())
