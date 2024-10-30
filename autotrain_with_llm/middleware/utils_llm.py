from fastapi import HTTPException, status
from autotrain_with_llm.models.manager_model import Managermodel
from logging import error
from groq import Groq
import textwrap
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_DIRECTORY = os.path.join(BASE_DIR, "../llm/utils/groq_api_key.txt")
TEXT_MODEL_TO_LLM_DIRECTORY = os.path.join(BASE_DIR, "../llm/utils/text_model_to_llm.txt")

def build_status_and_result_model(manager_model: Managermodel, step: int):
    if step == -1:
        status_model = "O treinamento do modelo foi iniciado, porém apresentou uma falha durante o treinamento"
        result_model = f"O modelo apresentou o seguinte erro: {manager_model.error}"
    
    if step == 1:
        status_model = "O modelo está em processo de treinamento"
        result_model = "O resultado do modelo será exibido somente após o final do treinamento"
    
    if step == 2:
        status_model = "O treinamento do modelo foi concluído"
        result_model = f"""
            Após o treinamento, as métricas de desempenho do modelo foram as seguintes:
            * Classes encontradas no Treinamento: ['glioma', 'meningioma', 'pituitary tumor']
            * Acurácia no Conjunto de Treinamento: {manager_model.model_used.test_accuracy * 100:.2f}%
            * Acurácia no Conjunto de Validação: {manager_model.model_used.val_accuracy * 100:.2f}%
            * Perda (Loss) no Conjunto de Treinamento: {manager_model.model_used.test_loss}
            * Perda (Loss) no Conjunto de Validação: {manager_model.model_used.val_loss}
            * Matriz de Confusão Gerada: {manager_model.model_used.confusion_matrix_values}
            * Precisão (Precision): {manager_model.model_used.precision* 100:.2f}%
            * Revocação (Recall): {manager_model.model_used.recall * 100:.2f}%
            * F1-Score: {manager_model.model_used.f1 * 100:.2f}%
        """
    return status_model, result_model

def build_model_configuration_text(step: int):
    manager_model = Managermodel()
    
    status_model, result_model = build_status_and_result_model(manager_model, step)
    
    return f"""
        Status do treinamento: {status_model}
                    
        A seguir, segue informações a cerca do treinamento
        
        Modelo de treinamento utilizado: {manager_model.model_name}
        
        Configurações do Treinamento:
        * epochs: {manager_model.epochs}
        * shuffle: {manager_model.shuffle}
        * seed: {manager_model.seed}
        * batch_size: {manager_model.batch_size}
        
        Resultados do treinamento:
        {result_model}
    """

def generate_text_model_to_llm_in_file(step: int = 1) -> None:
    """
    Função responsável por gerar o arquivo contendo as informações acerca do treinamento do modelo 
    que será passada para o LLM posteriormente
    
    Parâmetros:
    ----------
        step (int): Indica a etapa ao qual o treinamento do modelo se encontra. As possíveis etapas são:
            0 -> O usuário ainda não inciou o treinamento de um modelo
            1 -> O usuário iniciou o treinamento do modelo e ele se encontra em processo de treinamento
            2 -> O modelo já finalizou o treinamento e está pronto para ser testado
            -1 -> O usuário iniciou o treinamento do modelo, porém o mesmo apresentou um erro durante o treinamento
            
    Retorno:
    ----------
        A Função Não possui retorno
    """ 
    
    os.makedirs(os.path.dirname(TEXT_MODEL_TO_LLM_DIRECTORY), exist_ok=True)
    
    with open(TEXT_MODEL_TO_LLM_DIRECTORY, 'w') as file:
        text = ""
        
        if step == 0:
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
                """ 
        else: 
            text = build_model_configuration_text(step)
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