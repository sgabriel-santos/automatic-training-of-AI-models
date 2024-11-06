from fastapi import APIRouter
from autotrain_with_llm.llm.llm_with_groq_and_chromadb import send_answer
from autotrain_with_llm.middleware.utils_llm import register_groq_api_key_in_file

router = APIRouter(tags=["llm"])

@router.get("/send_message")
async def send_message(text: str):
    return send_answer(text)

@router.post('/register_groq_api_key', status_code=204)
async def register_groq_api_key(api_key: str):
    register_groq_api_key_in_file(api_key.replace('"', "").strip())