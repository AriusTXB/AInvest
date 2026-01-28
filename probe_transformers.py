from transformers import pipeline
import transformers
print(f"Transformers version: {transformers.__version__}")
try:
    s = pipeline("summarization")
    print("Summarization task is available.")
except Exception as e:
    print(f"Error loading summarization: {e}")

from transformers.pipelines import SUPPORTED_TASKS
print("Supported tasks in this install:")
print(list(SUPPORTED_TASKS.keys()))
