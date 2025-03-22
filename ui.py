import streamlit as st
import tempfile
import fitz  # PyMuPDF
from summarizer import LLaMASummarizer
from chroma_manager import ChromaDBManager

# Initialize services
summarizer = LLaMASummarizer()
db_manager = ChromaDBManager()

st.title("📚 ChromaDB Knowledge Base with LLaMA Summarization")

# UI placeholders
doc_preview_placeholder = st.empty()  # Placeholder for extracted document preview
summary_placeholder = st.empty()  # Placeholder for summary output

# Check if document is in session state, if yes, skip re-upload
if 'uploaded_file' in st.session_state:
    uploaded_file = st.session_state.uploaded_file
else:
    uploaded_file = st.file_uploader("📂 Upload a document (PDF/TXT)", type=["pdf", "txt"])

# Session state variable to track the visibility of the stored documents
if 'show_documents' not in st.session_state:
    st.session_state.show_documents = False  # Initially set to False

# Button to toggle the display of stored documents
if st.button("📂 Show/Hide Stored Documents"):
    st.session_state.show_documents = not st.session_state.show_documents

# If "Show Documents" is True, display the stored documents
if st.session_state.show_documents:
    doc_list = db_manager.list_documents()  # Get list of stored documents
    if doc_list:
        st.write("### 📜 Stored Documents:")
        for doc_name in doc_list:
            # Create three columns for file name, view summary, and delete button
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                st.write(f"📄 **{doc_name}**")
            
            with col2:
                # Button to toggle summary visibility
                show_summary_button = st.button(f"👁️ View Summary of {doc_name}", key=f"view_summary_{doc_name}")
                
                # Check if the summary is already visible for this document
                if 'summary_visible' not in st.session_state:
                    st.session_state['summary_visible'] = {}  # Initialize if not exists

                # Toggle the visibility of summary
                if show_summary_button:
                    st.session_state['summary_visible'][doc_name] = not st.session_state['summary_visible'].get(doc_name, False)

            with col3:
                # Button to delete the document
                delete_button = st.button(f"❌ Delete {doc_name}", key=f"delete_{doc_name}")
                if delete_button:
                    # Trigger the deletion and refresh the UI
                    db_manager.delete_document(doc_name)
                    st.success(f"✅ Deleted {doc_name}.")
                    st.experimental_rerun()  # Refresh UI after deletion

            # If summary is visible, display it in a new line below the document
            if st.session_state['summary_visible'].get(doc_name, False):
                summary = db_manager.get_summary(doc_name)  # Get summary using the new method
                if summary:
                    st.write(f"### Summary for {doc_name}:")
                    st.write(summary)
                else:
                    st.write("⚠️ Summary not found.")
    else:
        st.write("⚠️ No documents stored in the database.")

# Handle document upload and summarization
if uploaded_file:
    # Check if the document is already stored in the knowledge base
    if db_manager.is_document_stored(uploaded_file.name):
        st.warning("⚠️ This document has already been processed and stored!")
        st.stop()

    # Store file in temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        file_path = temp_file.name

    # Extract text from the document
    ext = uploaded_file.name.split(".")[-1].lower()
    text = ""
    
    with st.spinner("📖 Extracting text from document..."):
        if ext == "pdf":
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text("text") for page in doc])
        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            st.error("❌ Unsupported file type.")
            st.stop()

    if not text.strip():
        st.error("❌ No text extracted from file!")
        st.stop()

    st.success("✅ Text extracted successfully!")
    doc_preview_placeholder.text_area("📜 Extracted Document Preview:", text[:500], height=200)

    # Summarize and Store
    with st.spinner("📝 Summarizing document... This might take a few seconds!"):
        summary = summarizer.summarize(text)

    if not summary.strip():
        st.error("❌ Summarization failed! Check model logs.")
        st.stop()

    st.success("✅ Summarization completed!")
    summary_placeholder.text_area("📃 **Summary Preview:**", summary, height=200)

    # Store the summary in the knowledge base
    with st.spinner("💾 Storing summary in ChromaDB..."):
        db_manager.add_summary(uploaded_file.name, summary)

    st.success("✅ Document summarized and stored in Knowledge Base!")

    # Reset the session state to clear the document state after summarization
    del st.session_state.uploaded_file

    # **Clear Extracted Document Preview after summarization**
    doc_preview_placeholder.empty()

# Query the Knowledge Base
query = st.text_input("🔍 Search the knowledge base")

if query:
    with st.spinner("🔎 Searching knowledge base..."):
        results = db_manager.search(query)

    # Filter out unwanted error message from the results (if any)
    

    if results:
        
        st.write("**🔍 Search Results:**")
        
        # Assuming the result is structured as a dictionary with a 'text' key or directly as text
        first_result = results[0]
        
        # If first_result is a dictionary, we are assuming the actual content is under a key like 'text' or 'content'
        if isinstance(first_result, dict):
            result_content = first_result.get('text', '')  # Adjust this key based on your actual data structure
        else:
            result_content = first_result  # If it's plain text, use it directly

        # Display the clean result content without index or unnecessary details
        st.write(result_content)
    else:
        st.warning("⚠️ No relevant information found.")
