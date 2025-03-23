# 🧠 RAG-Based Document Summarizer &  Interactive QueryBot 

**A Retrieval-Augmented Generation (RAG) system powered by ChromaDB and LLaMA models, featuring a Streamlit UI for document summarization and an interactive chatbot.**  

## 🚀 Features  

✅ **Upload & Process Documents** (PDF/TXT)  
✅ **Summarization** using **LLaMA (Ollama API)**  
✅ **FAQ Chatbot** with RAG-based retrieval  
✅ **ChromaDB** for **storing & querying** document knowledge  
✅ **Multi-Document Support** (store and query multiple files)  
✅ **Web UI** for seamless interaction 

## 🛠 Setup
1️⃣ Clone the repository  
```sh
git clone https://github.com/deviarati18/Document-Summarizer-BOT.git
cd Document-Summarizer-BOT

2️⃣ Create a Virtual Environment (Recommended)
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Streamlit UI
streamlit run ui.py

📌 How It Works
1️⃣ Upload a document (PDF/TXT).
2️⃣ The system extracts and summarizes content using LLaMA (Ollama API).
3️⃣ The summary is stored in ChromaDB for efficient retrieval.
4️⃣ When a user asks a question, the FAQ chatbot retrieves relevant text using RAG and generates an answer.
