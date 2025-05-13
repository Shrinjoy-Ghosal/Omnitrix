import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv

# ✅ Load API key securely
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

app = FastAPI()

class ChatbotRequest(BaseModel):
    query: str

async def clean_response(text: str, query: str) -> str:
    """Remove [INST] tokens & prevent Mixtral from repeating the question."""
    cleaned_text = re.sub(r"\[/?INST\]", "", text).strip()  # ✅ Remove [INST] and [/INST]

    # ✅ Remove repeated query from the response
    if query.strip().lower() in cleaned_text.lower():
        cleaned_text = cleaned_text.replace(query.strip(), "").strip()

    return cleaned_text

async def generate_answer(query: str) -> str:
    """Send query to Mixtral API and return a cleaned response."""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        response = requests.post(
            API_URL, json={"inputs": f"[INST] {query} [/INST]"}, headers=headers
        )

        if response.status_code == 200:
            raw_text = response.json()[0].get("generated_text", "No response.")
            return await clean_response(raw_text, query)  # ✅ Remove repeated question
        else:
            return f"❌ API Error {response.status_code}: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"❌ Request failed: {str(e)}"

@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    """Main chatbot endpoint."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    return {"answer": await generate_answer(request.query)}

@app.get("/")
def read_root():
    """Root endpoint to confirm API is running."""
    return {"message": "Omnitrix AI is live with Mixtral!"}