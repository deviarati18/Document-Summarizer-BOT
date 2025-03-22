import streamlit as st
import subprocess

class LLaMASummarizer:
    def __init__(self, model="llama3.1:8b"):
        """Initialize LLaMA model."""
        self.model = model

    def summarize(self, text):
        """Summarize the text using LLaMA."""
        command = ["ollama", "run", self.model, f"Summarize the following text in 2 or 3 paragraphs \n{text}"]
        result = subprocess.run(command, capture_output=True, text=True)  # Capture output
        if result.returncode == 0:
            return result.stdout.strip()  # Return the output of the model
        else:
            return "Error: Unable to summarize the document."

# UI for the document summarizer
def main():
    st.title("Document Summarizer with LLaMA")

    # Create the Summarizer object
    summarizer = LLaMASummarizer()

    # Input text from the user
    text_input = st.text_area("Enter text to summarize:", "")

    # Button to trigger summarization
    if st.button("Summarize"):
        if text_input:
            # Get the summary from LLaMA
            summary = summarizer.summarize(text_input)
            st.subheader("Summary:")
            st.write(summary)
        else:
            st.warning("Please enter some text to summarize.")

    # Knowledge base search
    query = st.text_input("🔍 Search the knowledge base")
    if query:
        with st.spinner("🔎 Searching knowledge base..."):
            results = search_knowledge_base(query)

        if results:
            # Directly display all the results without filtering
            st.write("**🔍 Search Results:**")
            for result in results:
                st.write(result)
        else:
            st.warning("⚠️ No results found.")


# Function simulating a knowledge base search (this should be replaced with actual search logic)
def search_knowledge_base(query):
    """Simulates a search query to a knowledge base or API."""
    # Simulated search results; replace with actual search query and results
    command = ["ollama", "run", "llama3.1:8b", f"Search the knowledge base for: {query}"]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Assuming the result is returned in a list-like format with multiple items
        return result.stdout.splitlines()  # Assuming each result is separated by newlines
    else:
        return []


# Run the app
if __name__ == "__main__":
    main()
