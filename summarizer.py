
# 🚀 AI-Powered Document Summarizer
# Created by Devi C. Arati (@deviarati18) | GitHub: https://github.com/deviarati18


import streamlit as st
import ollama  # Using Ollama API directly
import chromadb  # Vector database for storing & retrieving knowledge

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")  
collection = client.get_or_create_collection(name="documents")

class LLaMASummarizer:
    def summarize(self, text):
        """Generates a summary using the LLaMA 3 model."""
        prompt = f"Summarize the following text:\n\n{text}\n\nSummary:"
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response['message']['content'].strip()

    def generate_response(self, query, context):
        """Generates a response using LLaMA 3 with retrieved context."""
        prompt = f"""
        You are an AI assistant. Answer the user's question based on the provided knowledge.
        Context from stored documents:

        {context if context.strip() else "No relevant documents found."}

        User's question:
        {query}
        """

        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response['message']['content'].strip()

def store_summary(doc_name, summary):
    """Store or update document summaries in ChromaDB."""
    try:
        existing_docs = collection.get(ids=[doc_name])

        if existing_docs and "documents" in existing_docs and existing_docs["documents"]:
            collection.update(ids=[doc_name], documents=[summary])  # Update existing summary
            return f"✅ Updated summary for '{doc_name}'"
        else:
            collection.add(ids=[doc_name], documents=[summary])  # Store new summary
            return f"✅ Stored new summary for '{doc_name}'"
    except Exception as e:
        return f"❌ Error storing summary: {str(e)}"

def search_knowledge_base(query):
    """Search for relevant information in stored summaries."""
    try:
        results = collection.query(query_texts=[query], n_results=5)
        return results["documents"][0] if results and "documents" in results else []
    except Exception as e:
        return f"❌ Error retrieving data: {str(e)}"

def main():
    st.title("📚 AI Document Summarizer & FAQ Chatbot")

    summarizer = LLaMASummarizer()
    tab1, tab2 = st.tabs(["📂 Document Summarizer", "🤖 FAQ Chatbot"])

    with tab1:
        st.subheader("📂 Upload a document to summarize")
        uploaded_file = st.file_uploader("📂 Upload TXT", type=["txt"])
        
        if uploaded_file:
            with st.spinner("⏳ Extracting text & summarizing..."):
                text = uploaded_file.read().decode("utf-8")  
                summary = summarizer.summarize(text)  
                result_msg = store_summary(uploaded_file.name, summary)
                
                st.success(result_msg)
                st.subheader("📃 Summary:")
                st.text_area("📃 Generated Summary:", summary, height=200)

    with tab2:
        st.subheader("🤖 Ask me anything!")
        query = st.text_input("🔍 Type your question")

        if query:
            with st.spinner("🔎 Searching stored documents..."):
                retrieved_texts = search_knowledge_base(query)

            if retrieved_texts:
                context = "\n".join(retrieved_texts)  
                response = summarizer.generate_response(query, context)
                st.markdown(f"**🤖 Chatbot Response:**\n\n{response}")
            else:
                st.warning("⚠️ No relevant documents found. Try another question!")

# Run the app
if __name__ == "__main__":
    main()
