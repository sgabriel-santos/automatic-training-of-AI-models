from fastapi import APIRouter, Request
from autotrain_with_llm.models.manager_model import Managermodel
from fastapi import HTTPException, status
from typing import Dict, List
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "../ui/statics/images/training_files/train")

router = APIRouter(tags=["utils"])


@router.get('/is_training_model')
async def training_model():
    return Managermodel().is_training_model()

@router.get('/step')
async def get_step():
    return Managermodel().step

@router.get('/model_config')
async def get_model_config():
    return Managermodel().get_model_config()


@router.get("/images", response_model=Dict[str, List[str]])
async def get_image_paths():
    """
    Retorna uma lista com os caminhos de todas as imagens armazenadas no diretório local.
    """
    # Verifica se o diretório existe
    if not os.path.exists(IMAGES_DIR):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diretório não encontrado"
        )

    categories = {}
    
    # Percorre todos os diretórios e subdiretórios
    for category_name in os.listdir(IMAGES_DIR):
        category_path = os.path.join(IMAGES_DIR, category_name)
        
        # Verifica se é um diretório (ou seja, uma "categoria")
        if os.path.isdir(category_path):
            images = [
                os.path.join(category_name, file)  # Salva o caminho relativo
                for file in os.listdir(category_path)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))
            ]
            # Adiciona a lista de imagens à categoria no dicionário
            categories[category_name] = images

    return categories


@router.get("/api/image-url")
async def get_image_url(request: Request):
    image_url = request.url_for('static', path='images/training_files/train/')
    return image_url

@router.post('/verify_library/{package_name}')
async def verify_library(package_name: str):
    try:
        __import__(package_name)
        return True
    except ImportError:
        print(f"{package_name} não está instalado. Instalando...")
        # subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    finally:
        # globals()[package_name] = __import__(package_name)
        return False


@router.get('/printar')
async def printar():
    print('testando')
    print('Verificando saida do log')
    return True