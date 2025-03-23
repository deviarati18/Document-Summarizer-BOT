import streamlit as st
import tempfile
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
from summarizer import LLaMASummarizer
from chroma_db_manager import ChromaDBManager

# Initialize services
summarizer = LLaMASummarizer()
db_manager = ChromaDBManager()

st.title("📚 AI-Powered Document Summarizer & FAQ Chatbot")

# === 📌 Create Tabs ===
tab1, tab2 = st.tabs(["📂 Document Summarizer", "🤖 FAQ Chatbot"])

# ==============================
# 📂 TAB 1: DOCUMENT SUMMARIZER (Displays Summary)
# ==============================
with tab1:
    st.subheader("📂 Upload & Summarize Documents")

    uploaded_file = st.file_uploader("📂 Upload a PDF or TXT file", type=["pdf", "txt"])

    if uploaded_file:
        file_name = uploaded_file.name

        # Check file size limit (5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("❌ File size too large! Please upload a smaller file (max 5MB).")
            st.stop()

        # Check if document is already stored
        if db_manager.is_document_stored(file_name):
            st.warning("⚠️ This document has already been processed!")
            existing_summary = db_manager.get_summary(file_name)
            
            if existing_summary and isinstance(existing_summary, str) and existing_summary.strip():
                st.success("✅ Stored Summary:")
                st.text_area("📃 Summary:", existing_summary, height=200)
            else:
                st.warning("⚠️ No stored summary found for this document.")
        else:
            # Save uploaded file to temporary storage
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                file_path = temp_file.name

            # Extract text
            ext = file_name.split(".")[-1].lower()
            text = ""

            with st.spinner("📖 Extracting text..."):
                try:
                    if ext == "pdf":
                        def extract_text_from_pdf(file_path):
                            doc = fitz.open(file_path)
                            text = ""

                            for page in doc:
                                extracted_text = page.get_text("text")  # Get digital text
                                if not extracted_text.strip():
                                    # Perform OCR on scanned pages
                                    pix = page.get_pixmap()
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                    extracted_text = pytesseract.image_to_string(img)

                                text += extracted_text + "\n"

                            doc.close()
                            return text

                        text = extract_text_from_pdf(file_path)

                    elif ext == "txt":
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                except Exception as e:
                    st.error(f"❌ Error extracting text: {e}")
                    text = ""

            # Clean up temp file
            os.remove(file_path)

            if text.strip():
                st.success("✅ Text extracted successfully!")

                # Summarize
                with st.spinner("📝 Summarizing document..."):
                    summary = summarizer.summarize(text)

                if summary.strip():
                    st.success("✅ Summary generated!")
                    st.text_area("📃 Summary:", summary, height=200)

                    # Store in ChromaDB
                    with st.spinner("💾 Storing in Knowledge Base..."):
                        try:
                            success_message = db_manager.add_summary(file_name, summary)
                            st.success(success_message)
                        except Exception as e:
                            st.error(f"❌ Error storing summary: {e}")
                else:
                    st.error("❌ No summary generated!")
            else:
                st.error("❌ No text extracted!")

    # === 🗂 Toggle Button to Show/Hide Saved Documents ===
    if st.checkbox("📜 Show Saved Documents"):
        saved_docs = db_manager.list_documents() or []

        if saved_docs:
            selected_doc = st.selectbox("📂 Select a document:", saved_docs)

            if st.button("📖 View Summary"):
                with st.spinner("🔍 Retrieving summary..."):
                    summary = db_manager.get_summary(selected_doc)

                if summary and isinstance(summary, str) and summary.strip():
                    st.text_area("📃 Stored Summary:", summary, height=200)
                else:
                    st.warning("⚠️ No summary found!")

            # Option to delete the document
            if st.button("🗑 Delete Document"):
                db_manager.delete_document(selected_doc)
                st.success(f"✅ Deleted {selected_doc}. Refresh the page to update the list.")
        else:
            st.info("ℹ️ No saved documents found.")

# ============================
# 🤖 TAB 2: FAQ CHATBOT (Answer Only)
# ============================
with tab2:
    st.subheader("🤖 FAQ Chatbot")

    # Ensure session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for msg in st.session_state.messages:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

    # User input
    query = st.text_input("Ask me anything about stored documents...")

    if query:
        # Store user query
        st.session_state.messages.append({"role": "user", "content": query})
        st.markdown(f"**User:** {query}")

        # Retrieve knowledge from ChromaDB
        with st.spinner("🔎 Searching knowledge base..."):
            results = db_manager.search(query, n_results=3)  # Fetch top 3 relevant docs

        if results and "documents" in results and results["documents"]:
            st.success(f"📖 Found {len(results['documents'])} relevant document(s).")

            # Extract only the relevant document texts
            context = "\n\n".join(results["documents"][0])
        else:
            st.warning("⚠️ No relevant documents found.")
            context = ""

        # RAG: Generate response using retrieved context (Only Answer, No Summary)
        with st.spinner("🤖 Thinking..."):
            answer = summarizer.generate_response(query, context)

        st.markdown(f"""
        **🤖 Assistant:**  
        📢 `{answer}`
        """)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": answer})
