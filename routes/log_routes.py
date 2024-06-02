from fastapi import APIRouter, Request, status
from starlette.responses import RedirectResponse, HTMLResponse, StreamingResponse
import sys
from io import StringIO
from fastapi.templating import Jinja2Templates
from middleware import utils_log

router = APIRouter(tags=["logs"])

templates = Jinja2Templates(directory="ui/templates")

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