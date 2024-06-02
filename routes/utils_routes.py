from fastapi import APIRouter
from models.manager_model import Managermodel
import sys

router = APIRouter(tags=["utils"])


@router.get('/is_training_model')
async def training_model():
    return Managermodel().is_training_model()

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