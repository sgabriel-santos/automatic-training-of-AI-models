from fastapi import HTTPException, status
from logging import error
from groq import Groq
import os.path

API_KEY_DIRECTORY = 'llm/groq_api_key.txt'
TEXT_MODEL_TO_LLM_DIRECTORY = 'llm/text_model_to_llm.txt'

def generate_text_model_to_llm(data: dict, state = 1) -> None:
    """
    Função responsável por gerar o arquivo contendo as informações acerca do treinamento do modelo que será passada para o LLM posteriormente
    
    Parâmetros:
    ----------
        data (dict): Contêm as informações relevantes sobre o modelo treinado ou em treinamento
        state (int): Representa o estado atual do treinamento. Pode variar entre 1 e 3.
            1 - Treinamento não iniciado;  
            2- Modelo está em treinamento;  
            3 - Modelo treinado e pronto para uso;
            
    Retorno:
    ----------
        A Função Não possui retorno
    """ 
    
    with open(TEXT_MODEL_TO_LLM_DIRECTORY, 'w') as file:
        # file.write('Treinamento\n')
        # file.write('A seguir, apresento o treinamento do modelo, onde são definidos valores específicos para os principais parâmetros de treinamento.\n\n')
        file.write(f"Status do treinamento: O modelo está em processo de treinamento\n\n")
        file.write(f"A seguir, segue informações a cerca do treinamento\n\n")
        file.write(f"Modelo de treinamento utilizado: {data['model_name']}\n\n")
        
        file.write('Configurações do Treinamento\n')
        file.write(f"* epochs: {data['epochs']}\n")
        file.write(f"* shuffle: {data['shuffle']}\n")
        file.write(f"* seed: {data['seed']}\n")
        file.write(f"* batch_size: {data['batch_size']}\n\n")
        
def get_text_model_to_llm():
    file_exists = os.path.isfile(TEXT_MODEL_TO_LLM_DIRECTORY)
    
    if not file_exists:
        return """
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
        """
    
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