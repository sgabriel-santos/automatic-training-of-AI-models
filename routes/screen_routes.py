from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from models.image_classification import ImageClassification
import inspect

# Model Imported
image_classification = ImageClassification()

router = APIRouter(tags=["screens"])

templates = Jinja2Templates(directory="ui/templates")

@router.get('/')
async def home_screen(request: Request):
    return templates.TemplateResponse("form.html", {"request": request,  "name": "Teste Jinja"})


@router.get('/source_code')
async def source_code_screen(request: Request):
    function_code = inspect.getsource(image_classification.fit)
    return templates.TemplateResponse("source_code.html", {"request": request, "function_code": function_code})


@router.get('/test_model')
async def test_model_screen(request: Request):
    return templates.TemplateResponse("test_model.html", {"request": request})
