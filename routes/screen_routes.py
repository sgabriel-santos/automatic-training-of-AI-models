from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from models.manager_model import Managermodel
import inspect

# Model Imported
manager_model = Managermodel()

router = APIRouter(tags=["screens"])

templates = Jinja2Templates(directory="ui/templates")

@router.get('/')
async def home_screen(request: Request):
    return templates.TemplateResponse("form.html", {"request": request,  "name": "Teste Jinja"})


@router.get('/source_code')
async def source_code_screen(request: Request):
    function_code = "Necessário iniciar o treinamento com um dos modelos para visualizar o seu código"
    if manager_model.model_used:
        function_code = inspect.getsource(manager_model.model_used.fit_model)
    return templates.TemplateResponse("source_code.html", {"request": request, "function_code": function_code})


@router.get('/test_model')
async def test_model_screen(request: Request):
    with open('models/results/metrics.txt', 'r') as file:
        vl, va, tl, ta = file.readline().split(' ')
    
    return templates.TemplateResponse(
        "test_model.html", 
        {
            "request": request, 
            "validation_loss": vl, 
            "validation_accuracy": va, 
            "test_loss": tl, 
            "test_accuracy": ta
        })
