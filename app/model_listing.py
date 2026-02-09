import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

# List available models
try:
    pager = client.models.list(config={"page_size": 50})
    print("Available Gemini models:")
    for model in pager:
        print(f"- {model.name}")
except Exception as e:
    print("Error listing models:", e)
