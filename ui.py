import streamlit as st
import tempfile
from PyPDF2 import PdfReader
from app.summarizer import LLaMASummarizer
from app.chroma_manager import ChromaDBManager

# Initialize services
summarizer = LLaMASummarizer()
db_manager = ChromaDBManager()

st.title("📚 ChromaDB Knowledge Base with LLaMA Summarization")

# Upload Document
uploaded_file = st.file_uploader("📂 Upload a document (PDF/TXT)", type=["pdf", "txt"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        file_path = temp_file.name

    # Extract text
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        st.error("❌ Unsupported file type.")
        st.stop()

    # Summarize & Store
    summary = summarizer.summarize(text)
    db_manager.add_summary(uploaded_file.name, summary)
    
    st.success("✅ Document summarized and stored!")
    st.write(summary)

# Query the Knowledge Base
query = st.text_input("🔍 Search the knowledge base")
if query:
    results = db_manager.search(query)
    if results:
        st.write("**Top results:**")
        for res in results:
            st.write(res)
    else:
        st.write("⚠️ No relevant information found.")
