from dotenv import load_dotenv
load_dotenv()
import os

print("API_KEY:", os.getenv("OPENAI_API_KEY")[:20] + "...")
print("MODEL_NAME:", os.getenv("MODEL_NAME"))
print("API_BASE_URL:", os.getenv("API_BASE_URL"))