from fastapi import APIRouter
from llm.llm_with_groq_and_chromadb import send_answer
from middleware.utils_llm import register_groq_api_key_in_file

router = APIRouter(tags=["llm"])

@router.get("/send_message")
async def send_message(text: str):
    return send_answer(text)

@router.post('/register_groq_api_key')
async def register_groq_api_key(api_key: str):
    register_groq_api_key_in_file(api_key)