from fastapi import status, BackgroundTasks, UploadFile, File, HTTPException, status, Form, APIRouter
from starlette.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.responses import JSONResponse
from llm_image_classifier.models.manager_model import Managermodel
from llm_image_classifier.middleware import utils_log, utils_llm
from typing import Optional
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
    dataset_config_mode: str = Form(...),
    train_dataset_path: Optional[str] = Form(None),
    valid_dataset_path: Optional[str] = Form(None),
    file_training: Optional[UploadFile] = File(None),
    file_validation: Optional[UploadFile] = File(None),
    file_training_images: Optional[list[UploadFile]] = File(None),
):
    """
    Endpoint de configuração do modelo a ser treinado.
    Aqui, os parâmetros de configração devem ser passados para que o ambiente seja preparado com os parâmetros e o dataset correto.
    Posteriormente, o treinamento pode ser inicializado por meio do endpoint /fit_model
    
    Parameters:
        - dataset_config_mode (str): Este parâmetro representa o modelo com o usuário deseja configurar o dataset. As opções disponíveis, são:
            
            - upload-dataset: Informa que o usuário realizou a importação do dataset (formato .zip)
                - Nesta opção, o dataset deverá ser passado pelo usuário através dos parâmetros file_training e file_validation
            
            - dataset-path: Informa que o usuário deseja utilizar um dataset existente na máquina que a ferramenta está sendo executada
                - Nesta opção, o caminho do dataset de treinamento e validação devem ser passados através dos parãmetros train_dataset_path e valid_dataset_path
            
            - manual-config: Informa que o usuário criou o dataset manualmente através de importações de imagens
                - Nesta opção, as imagens do dataset devem ser passadas através do parâmetro file_training_images
                - Um detalhe importanto, o nome da imagem deve conter inicialmente o nome da classe. Por exemplo, o arquivo com o nome classe1/image.png indica que a imagem é da classe 1
    """
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
            'dataset_config_mode': dataset_config_mode,
            'file_training': file_training,
            'file_validation': file_validation,
            'train_dataset_path': train_dataset_path,
            'valid_dataset_path': valid_dataset_path,
            'file_training_images': file_training_images
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
    if Managermodel().step != 4:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Must have completed training of a model"
        )
        
    response = Managermodel().predict(image)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao realizar a predição da imagem"
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