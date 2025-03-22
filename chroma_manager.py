import chromadb

class ChromaDBManager:
    def __init__(self, db_path="./chroma_db"):  # Set a fixed path for persistence
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("document_summaries")

    def list_documents(self):
        """List stored document names without fetching full text"""
        stored_docs = self.collection.get(include=["metadatas"])  # Fetch only metadata
        metadatas = stored_docs.get("metadatas", [])  # Ensure it's a list
        return [doc["filename"] for doc in metadatas if isinstance(doc, dict) and "filename" in doc]

    def is_document_stored(self, document_name):
        """Check if a document is already in the database"""
        stored_documents = self.list_documents()  # Assuming list_documents() returns a list of document names
        return document_name in stored_documents

    def add_summary(self, doc_name, summary):
        """Add a document summary to ChromaDB."""
        self.collection.add(
            ids=[doc_name], 
            documents=[summary], 
            metadatas=[{"filename": doc_name}]  # Store filename in metadata
        )
        
    def get_summary(self, doc_name):
        """Retrieve the summary of a document."""
        try:
            results = self.collection.get(ids=[doc_name])  # Corrected to access collection
            if results["documents"]:  # Check if there are documents returned
                print(f"✅ Retrieved summary for {doc_name}.")
                return results["documents"][0]  # Return the summary stored in the database
            else:
                print(f"⚠️ No summary found for {doc_name}.")
            return None
        except Exception as e:
            print(f"❌ Error retrieving summary for {doc_name}: {e}")
            return None
    
    def delete_document(self, document_name):
        """Deletes a document from the ChromaDB collection."""
        try:
            # Remove the document from the collection based on its name (or ID)
            self.collection.delete(ids=[document_name])
            print(f"Document '{document_name}' has been deleted from ChromaDB.")
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
  
    def clear_knowledgebase(self):
        """Clear all documents from the knowledge base"""
        self.client.delete_collection("document_summaries")  # Delete the collection
        self.collection = self.client.get_or_create_collection("document_summaries")  # Recreate it
        
    def search(self, query, n_results=3):
        """Search the knowledge base and return only the first result's content."""
        try:
            # Perform the query
            results = self.collection.query(query_texts=[query], n_results=n_results)

            # Check if there are any documents in the results and return only the content of the first document
            if "documents" in results and results["documents"]:
                return results["documents"][0]  # Return only the first document's content
            else:
                return ""  # Return an empty string if no results found
        except Exception as e:
            print(f"Error during search: {e}")
            return ""  # Return empty string in case of error

# Check if data is stored
if __name__ == "__main__":
    db = ChromaDBManager()
    print("📚 Current Knowledge Base:", db.list_documents())
