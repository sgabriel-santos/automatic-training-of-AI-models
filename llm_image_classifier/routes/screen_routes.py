from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from llm_image_classifier.models.manager_model import Managermodel
from llm_image_classifier.models.save_files_class import SaveFiles
import inspect
import os

# Model Imported
manager_model = Managermodel()

router = APIRouter(tags=["screens"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(BASE_DIR, "../ui/templates")
templates = Jinja2Templates(directory=templates_path)

@router.get('/')
async def home_screen(request: Request):
    return templates.TemplateResponse("home.html", {"request": request,  "name": "Teste Jinja"})

@router.get('/form')
async def form_screen(request: Request):
    return templates.TemplateResponse("form.html", {"request": request,  "name": "Teste Jinja"})


@router.get('/source_code')
async def source_code_screen(request: Request):
    function_code = "Necessário iniciar o treinamento com um dos modelos para visualizar o seu código"
    if manager_model.model_used:
        function_code = inspect.getsource(manager_model.model_used.fit_model)
    return templates.TemplateResponse("source_code.html", {"request": request, "function_code": function_code})


@router.get('/dataset')
async def dataset(request: Request):
    return templates.TemplateResponse("dataset.html", {"request": request, "name": "Dataset"})


@router.get('/result_model')
async def result_model_screen(request: Request):
    try:
        metrics = SaveFiles().get_metrics()
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Não foi possível localizar as informações de métricas do modelo treinado"
            )
        vl, va, tl, ta = metrics
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao coletar informações das métricas"
        )
        
    return templates.TemplateResponse(
        "result_model.html", 
        {
            "request": request, 
            "validation_loss": f"{float(vl):.3f}", 
            "validation_accuracy": f"{float(va) * 100:.2f}", 
            "test_loss": f"{float(tl):.3f}", 
            "test_accuracy": f"{float(ta) * 100:.2f}"
        })

@router.get('/test_model')
async def test_model(request: Request):
    return templates.TemplateResponse("test_model.html", {"request": request, "name": "Dataset"})