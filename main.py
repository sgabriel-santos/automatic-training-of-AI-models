from fastapi import FastAPI, status, BackgroundTasks, UploadFile, File, HTTPException, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.responses import JSONResponse
from models.manager_model import Managermodel
from middleware import utils_log
from routes import log_routes, screen_routes, utils_routes
import sys
import os

app = FastAPI()
app.include_router(log_routes.router)
app.include_router(screen_routes.router)
app.include_router(utils_routes.router)

# UI Configuration
templates = Jinja2Templates(directory="ui/templates")
app.mount("/static", StaticFiles(directory="ui/statics"), name="static")


@app.post('/fit_model', response_class=HTMLResponse)
async def fit_model(
    background_tasks: BackgroundTasks,
    name_model: str = Form(...),
    epochs: int = Form(...),
    shuffle: bool = Form(...),
    seed: int = Form(...),
    batch_size: int = Form(...),
    file_training: UploadFile = File(...),
    file_validation: UploadFile = File(...)
):
    manager_model = Managermodel()
    model = manager_model.get_model(name_model)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with name {name_model} not found"  
        )

    try:
        data = {
            'model_name': name_model,
            'epochs': epochs,
            'shuffle': shuffle,
            'seed': seed,
            'batch_size': batch_size,
            'file_training': file_training,
            'file_validation': file_validation
        }
        model.get_parameters(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error building parameters: {str(e)}"  
        )

    sys.stdout = utils_log.stdout_buffer
    background_tasks.add_task(model.fit_model, manager_model)
    url = app.url_path_for('home_screen')
    return RedirectResponse(url=url, status_code=status.HTTP_200_OK)


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    model = Managermodel().get_model('image_classification')
    return model.predict(image)


@app.get("/download_model")
async def download_model():
    file_path = "models/results/image_classification.model.keras"

    if os.path.exists(file_path):
        return FileResponse(file_path, filename="model.keras")
    return {"error": "File not found"}

import os
import zipfile
import shutil

@app.post("/upload-zip")
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
