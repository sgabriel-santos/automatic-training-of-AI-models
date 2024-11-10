from fastapi import HTTPException, status
from autotrain_with_llm.models.models import name_to_model
from autotrain_with_llm.models.abstract_model_class import ImageClassification
from tf_keras.models import load_model
from fastapi import UploadFile
from autotrain_with_llm.middleware.utils_os import exists_directory
import shutil
import zipfile
import os
import numpy as np
from PIL import Image
import json

class Managermodel:
    """
    Classe Singleton responsável por gerenciar o treinamento do modelo 
    de acordo com o Modelo de treinamento escolhido pelo usuário
    """
    
    _instance = None
    training_model = False
    
    TRAINING_DIR=None
    TEST_DIR=None
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_NAME_RESULT = os.path.join(BASE_DIR, "results/image_classification.model.keras")
    
    model_name = None
    epochs = None
    shuffle = None
    seed = None
    batch_size = None
    im_shape = (250,250)
    classes = []
    
    is_absolute_path: bool = None
    ready_parameters = False
    
    model_used: ImageClassification | None = None
    
    error = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.training_model = False
        return cls._instance
    
    
    def set_model_to_be_used(self, model_name: str) -> bool:
        """
        Responsável por escolher a classe de treinamento ao qual será utilizada para o treinamento
        
        Argumentos:
            - model_name (str): Nome do modelo a ser utilizado para o treinamento
        
        Retorno:
            - Boolean. True, caso tenha sido encontrao um modelo de treinamento válido 
              e False caso contrário
        """
        
        if model_name not in name_to_model: return False
        self.model_used = name_to_model[model_name]()
        return True


    def set_parameters_to_training_model(self, data: dict) -> None:
        """
        Responsável por realizar a configuração dos parâmetros 
        a serem utilizados para o treinamento do modelo
        
        Argumentos:
            - data (dict): Dicionário contendo as configurações de parâmetros
            
        Retorno:
            - None
        """
        
        self.model_used.set_parameters_to_training_model(data)
        self.model_name = data['model_name']
        self.epochs = data['epochs']
        self.shuffle = data['shuffle']
        self.seed = data['seed']
        self.batch_size = data['batch_size']
        
        self.TRAINING_DIR = os.path.join(self.BASE_DIR, "../ui/statics/images/training_files/train")
        self.TEST_DIR = os.path.join(self.BASE_DIR, "../ui/statics/images/training_files/test")
        self.is_absolute_path = data['is_absolute_path']
        
        if not self.is_absolute_path:
            if(data['file_training'].filename): self.classes = self.__save_files(data['file_training'], 'train')
            if(data['file_validation'].filename): 
                if self.__save_files(data['file_validation'], 'test') != self.classes:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Os arquivos de treinamento e teste não possuem as mesmas classes"
                    )
        else:
            is_valid_directory, current_class = self.__is_valid_directory_structure(data['train_dataset_path'])
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de treinamento enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
            self.classes = current_class
            is_valid_directory, current_class = self.__is_valid_directory_structure(data['valid_dataset_path'])
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de teste enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
            if current_class != self.classes:
                raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Os arquivos de treinamento e teste não possuem as mesmas classes"
                    )
                
            self.__copy_directory(data['train_dataset_path'], self.TRAINING_DIR)
            self.__copy_directory(data['valid_dataset_path'], self.TEST_DIR)
            self.ready_parameters = True
    
    
    def is_training_model(self) -> bool:
        """
        Verifica se há um modelo está em processo de treinamento
        
        Argumentos:
            - N/A
        
        Retorno:
            - Bool. True, caso haja um modelo em treinamento. False, caso contrário
            
        """
        return self.training_model
    
        
    def fit_model(self, generate_text_model_to_llm_in_file):
        self.__update_training_model(True)
        generate_text_model_to_llm_in_file(1)
        try:
            print('Iniciando fluxo de treinamento do modelo')
            if not exists_directory(self.TRAINING_DIR):
                print('Error: Diretório de treinamento não encontrado')
                self.error = "Diretório de treinamento não encontrado"
                self.__update_training_model(False)
                generate_text_model_to_llm_in_file(-1)
                return False
            
            if(not exists_directory(self.TEST_DIR)):
                print('Error: Diretório de test não encontrado')
                self.error = "Diretório de test não encontrado"
                self.__update_training_model(False)
                generate_text_model_to_llm_in_file(-1)
                return False
            
            history = self.model_used.fit_model()
            
        except Exception as e:
            self.__update_training_model(False)
            print('Parando fluxo de treinamento do modelo.')
            print(f'Detalhe da excessão: {e}')
            self.error = e
            generate_text_model_to_llm_in_file(-1)
            raise    
        
        print('Modelo Treinado com sucesso')
        try:
            self.model_used.test_model(history)
        except Exception as e:
            self.__update_training_model(False)
            print('Erro durante realização de testes no modelo')
            print(f'Detalhe da excessão: {e}')
            self.error = f"Erro durante realização de testes no modelo. Detalhe da excessão: {e}"
            generate_text_model_to_llm_in_file(-1)
            raise
            
        self.__update_training_model(False)
        generate_text_model_to_llm_in_file(2)
        
        
    def predict(self, image) -> dict | None:
        """
        Realiza a predição da classe para uma determinada imagem importada pelo usuário
        
        Retorno:
            Dicionário contendo classe da imagem importada ou None caso o modelo ainda não tenha sido treinado
        """
        model = load_model(self.MODEL_NAME_RESULT)
        processed_image = self.__load_and_process_image(image.file)
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])
        
        classes = self.get_classes()

        return {"predicted_class": classes[int(predicted_class)]}
    

    def get_classes(self) -> list[str]:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_class_dir = os.path.join(BASE_DIR, "results/classes.txt")
        with open(file_class_dir, 'r') as file:
            line = file.readline().replace("'", '"')
            return json.loads(line)
        
    def get_model_config(self):
        return {
            "model_name": self.model_name,
            "epochs": self.epochs,
            "shuffle": self.shuffle,
            "seed": self.seed,
            "batch_size": self.batch_size
        }
    
    
    def __update_training_model(self, is_training: bool) -> None:
        """
        Atualiza o status de treinamento do modelo
        
        Argumentos:
            - is_training (bool): True, informa que há um modelo em processo de treinamento. 
              False, caso contrário
        
        Retorno:
            - None
        """ 
        self.training_model = is_training

    
    def __load_and_process_image(self, img):
        img = Image.open(img)
        
        if img.mode != 'RGB': img = img.convert('RGB')
        
        img = img.resize(self.im_shape)
        img_array = np.array(img)
        img_array = img_array / 255.0  # Normalização
        img_array = np.expand_dims(img_array, axis=0)  # Adicionar dimensão do batch
        return img_array
    
    
    def __save_files(self, file: UploadFile, prefix_path: str) -> list[str]:
        # Verifica se o arquivo é um zip
        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="File must be a ZIP"
            )

        # Define o caminho onde o zip será salvo temporariamente
        temp_zip_path = "temp.zip"
        
        # Salva o arquivo zip temporariamente
        with open(temp_zip_path, "wb") as temp_zip:
            shutil.copyfileobj(file.file, temp_zip)
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Remove o diretório e todo o seu conteúdo
        extract_dir = os.path.join(BASE_DIR, f"../ui/statics/images/training_files/{prefix_path}")
        shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

        # Descompacta o arquivo zip
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        is_valid_directory, classes = self.__is_valid_directory_structure(extract_dir)

        if not is_valid_directory:
            mode = "treinamento" if prefix_path == 'train' else "teste"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O dataset de {mode} enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
            )
        
        # Remove o arquivo zip temporário
        os.remove(temp_zip_path)
        return classes
    
    def __copy_directory(self, source, destination):
        """
        Copia um diretório de uma origem para um destino.
        
        Parâmetros:
        source (str): Caminho do diretório de origem.
        destination (str): Caminho do diretório de destino.
        """
        # Verifica se o diretório de origem existe
        if not os.path.exists(source):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diretório de origem '{source}' não existe."
            )

        # Verifica se o diretório de destino já existe
        if os.path.exists(destination):
            print(f"Diretório de destino '{destination}' já existe. Removendo...")
            shutil.rmtree(destination)  # Remove o diretório destino, se já existir

        try:
            # Copia todo o conteúdo do diretório de origem para o destino
            shutil.copytree(source, destination)
            print(f"Diretório copiado com sucesso de '{source}' para '{destination}'.")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ocorreu um erro ao copiar o diretório: {e}"
            )
            
        
    def __is_valid_directory_structure(self, base_dir):
        """
        Verifica se o diretório descompactado possui a estrutura correta:
            - O diretório base existe
            - Vários diretórios estão presentes no diretório base
            - Cada diretório contém múltiplas imagens
        """
        # Verifica se o diretório base existe
        if not os.path.exists(base_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diretório '{base_dir}' não existe."
            )
    
        classes = []
        for root, dirs, files in os.walk(base_dir):
            # Certifique-se de que existem subdiretórios no     diretório base
            if root == base_dir and not dirs:
                return False
            
            # Certifique-se de que cada subdiretório contém imagens
            for dir_name in dirs:
                classes.append(dir_name)
                dir_path = os.path.join(root, dir_name)
                if not any(file.lower().endswith(('.png', '.jpg', '.jpeg')) for file in os.listdir(dir_path)):
                    return False, []
        return True, classes