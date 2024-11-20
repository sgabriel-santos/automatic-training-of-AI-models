from fastapi import APIRouter, Request, status
from starlette.responses import RedirectResponse, HTMLResponse, StreamingResponse
from io import StringIO
from fastapi.templating import Jinja2Templates
from llm_image_classifier.middleware import utils_log
import sys
import os

router = APIRouter(tags=["logs"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(BASE_DIR, "../ui/templates")
templates = Jinja2Templates(directory=templates_path)

@router.get("/logs", response_class=StreamingResponse)
async def get_logs():
    captured_logs = utils_log.stdout_buffer.getvalue()
    return StreamingResponse(iter([captured_logs]), media_type="text/plain")

@router.get("/reset-logs")
async def reset_logs():
    sys.stdout = utils_log.original_stdout
    utils_log.stdout_buffer = StringIO()
    url = router.url_path_for('log_screen')
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logs_screen", response_class=HTMLResponse)
async def log_screen(request: Request):
    # Retornar os logs como uma resposta de streaming
    return  templates.TemplateResponse("logs.html", {"request": request,  "name": "Teste Jinja"})