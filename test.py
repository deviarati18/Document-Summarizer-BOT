import subprocess
import sys
import os

# Disable ANSI escape codes (can cause the issue)
os.system("set TERM=vt100")

# Set UTF-8 mode
os.system("chcp 65001 > nul")

def run_ollama(prompt):
    try:
        # Redirect stderr to devnull to avoid console errors
        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen(
                ["ollama", "run", "llama3.1:8b", prompt],
                stdout=subprocess.PIPE,
                stderr=devnull,  # redirecting stderr
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            stdout, _ = process.communicate()

            if stdout:
                sys.stdout.write(stdout + "\n")
                sys.stdout.flush()

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.stderr.flush()

if __name__ == "__main__":
    run_ollama("hello world")
