from fastapi import HTTPException, status
from models.manager_model import Managermodel
from logging import error
from groq import Groq
import textwrap
import os

API_KEY_DIRECTORY = 'llm/utils/groq_api_key.txt'
TEXT_MODEL_TO_LLM_DIRECTORY = 'llm/utils/text_model_to_llm.txt'

def build_status_and_result_model(manager_model: Managermodel):
    status_model = "O modelo está em processo de treinamento"
    result_model = "O resultado do modelo será exibido somente após o final do treinamento"
    if not manager_model.is_training_model():
        status_model = "O treinamento do modelo foi concluído"
        result_model = "Estamos trabalhando para montar as informações do resultado do modelo"
    return status_model, result_model

def build_model_configuration_text():
    manager_model = Managermodel()
    status_model, result_model = build_status_and_result_model(manager_model)
    
    return f"""
        Status do treinamento: {status_model}
                    
        A seguir, segue informações a cerca do treinamento
        
        Modelo de treinamento utilizado: {manager_model.model_name}
        
        Configurações do Treinamento:
        * epochs: {manager_model.epochs}
        * shuffle: {manager_model.shuffle}
        * seed: {manager_model.seed}
        * batch_size: {manager_model.batch_size}
        
        Resultado:
        {result_model}
    """

def generate_text_model_to_llm_in_file(is_training_started = True) -> None:
    """
    Função responsável por gerar o arquivo contendo as informações acerca do treinamento do modelo 
    que será passada para o LLM posteriormente
    
    Parâmetros:
    ----------
        is_training_started (bool): Indica se já foi iniciado o treinamento do modelo.
            
    Retorno:
    ----------
        A Função Não possui retorno
    """ 
    
    os.makedirs(os.path.dirname(TEXT_MODEL_TO_LLM_DIRECTORY), exist_ok=True)
    
    with open(TEXT_MODEL_TO_LLM_DIRECTORY, 'w') as file:
        text = """
                Status do treinamento: O usuário ainda não iníciou o treinamento de um modelo
                
                As opções de modelos a serem escolhidas pelo usuários são:
                * XCeption
                * VGG19
                * ResNet50
                * MobileNet
                * InceptionV3
                
                Os parâmetros que o usuário pode configurar são:
                * Épocas
                * Seed
                * Batch Size
            """ if not is_training_started else build_model_configuration_text()
        file.write(textwrap.dedent(text))
    
def get_text_model_to_llm():
    try:
        with open(TEXT_MODEL_TO_LLM_DIRECTORY, 'r') as file:
            return ''.join(file.readlines())
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao recuperar as informações do treinamento do modelo"
        )
        
def register_groq_api_key_in_file(api_key_value: str):
    try:
        with open(API_KEY_DIRECTORY, 'w') as file:
            file.write(api_key_value)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao registrar a API Key"
        )
        
def get_groq_api_key():
    try:
        with open(API_KEY_DIRECTORY, 'r') as file:
            return file.readline()
    except FileNotFoundError:
        error('API Key do Groq não configurada')
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="API Key do Groq não configurada"
        )
    
def get_llm_instance():
    groq_api_key = get_groq_api_key()
    try: return Groq(api_key=groq_api_key)
    except:
        error('Não foi possível se conectar à API do Groq, certifique que a chave utilizada esteja correta')
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Não foi possível se conectar à API do Groq"
        )