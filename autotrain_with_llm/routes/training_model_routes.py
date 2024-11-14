from fastapi import status, BackgroundTasks, UploadFile, File, HTTPException, status, Form, APIRouter
from starlette.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.responses import JSONResponse
from autotrain_with_llm.models.manager_model import Managermodel
from autotrain_with_llm.middleware import utils_log, utils_llm
import sys
import os
import zipfile
import shutil

router = APIRouter(tags=["training_model"])

@router.post('/configure_model', response_class=HTMLResponse)
async def configure_model(
    model_name: str = Form(...),
    epochs: int = Form(...),
    shuffle: bool = Form(...),
    seed: int = Form(...),
    batch_size: int = Form(...),
    is_absolute_path: bool = Form(...),
    train_dataset_path: str = Form(...),
    valid_dataset_path: str = Form(...),
    file_training: UploadFile = File(...),
    file_validation: UploadFile = File(...)
):
    manager_model = Managermodel()
    
    if manager_model.is_training_model():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Há um modelo em processo de treinamento"  
        )
    
    utils_llm.generate_text_model_to_llm_in_file(1)
    found_model = manager_model.set_model_to_be_used(model_name)

    if not found_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with name {model_name} not found"  
        )

    try:
        data = {
            'model_name': model_name,
            'epochs': epochs,
            'shuffle': shuffle,
            'seed': seed,
            'batch_size': batch_size,
            'is_absolute_path': is_absolute_path,
            'file_training': file_training,
            'file_validation': file_validation,
            'train_dataset_path': train_dataset_path,
            'valid_dataset_path': valid_dataset_path
        }
        manager_model.set_parameters_to_training_model(data)
        utils_llm.generate_text_model_to_llm_in_file(2)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error building parameters: {str(e)}"  
        )

    return RedirectResponse(url='/', status_code=status.HTTP_200_OK)


@router.post('/fit_model')
async def fit_model(
    background_tasks: BackgroundTasks,  
):
    manager_model = Managermodel()
    if not manager_model.ready_parameters:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Os Parâmetros de configuração do modelo não foram configurados"
        )
        
    sys.stdout = utils_log.stdout_buffer
    background_tasks.add_task(manager_model.fit_model, utils_llm.generate_text_model_to_llm_in_file)
    return True


@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    response = Managermodel().predict(image)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Must have completed training of a model"
        )
    return response

@router.get("/download_model")
async def download_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "../models/results/image_classification.model.keras")

    if os.path.exists(file_path):
        return FileResponse(file_path, filename="model.keras")
    return {"error": "File not found"}


@router.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    # Verifica se o arquivo é um zip
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a ZIP")

    # Define o caminho onde o zip será salvo temporariamente
    temp_zip_path = "temp.zip"
    
    # Salva o arquivo zip temporariamente
    with open(temp_zip_path, "wb") as temp_zip:
        shutil.copyfileobj(file.file, temp_zip)
    
    # Define o diretório onde os arquivos serão descompactados
    extract_dir = "extracted_files"
    os.makedirs(extract_dir, exist_ok=True)

    # Descompacta o arquivo zip
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Remove o arquivo zip temporário
    os.remove(temp_zip_path)
    
    return JSONResponse(content={"message": "File uploaded and extracted successfully"})