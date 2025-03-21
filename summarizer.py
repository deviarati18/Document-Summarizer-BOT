import subprocess

class LLaMASummarizer:
    def __init__(self, model="llama3.1:8b"):
        """Initialize LLaMA model."""
        self.model = model

    def summarize(self, text):
        """Summarize the text using LLaMA."""
        command = ["ollama", "run", self.model, f"Summarize the following text:\n{text}"]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()

# Usage Example:
if __name__ == "__main__":
    summarizer = LLaMASummarizer()
    summary = summarizer.summarize("Large language models are transforming AI.")
    print(summary)

