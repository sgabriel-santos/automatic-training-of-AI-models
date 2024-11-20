from fastapi import HTTPException, status
from autotrain_with_llm.models.models import name_to_model
from autotrain_with_llm.models.abstract_model_class import ImageClassification
from fastapi import UploadFile
from autotrain_with_llm.middleware.utils_os import exists_directory
import shutil
import zipfile
import os
import numpy as np
from PIL import Image
import json
import random
from collections import defaultdict

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
    number_of_file_per_class = {}
    step = 0
    
    dataset_config_mode: str = None
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
        self.dataset_config_mode = data['dataset_config_mode']
        
        if self.dataset_config_mode == 'upload-dataset':
            if(data['file_training'].filename): self.classes, number_of_train_images_per_class = self.__save_files(data['file_training'], 'train')
            if(data['file_validation'].filename):
                current_class, number_of_valid_images_per_class = self.__save_files(data['file_validation'], 'test')
                if current_class != self.classes:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Os arquivos de treinamento e validação não possuem as mesmas classes"
                    )
        elif self.dataset_config_mode == 'dataset-path':
            is_valid_directory, current_class, number_of_train_images_per_class = self.__is_valid_directory_structure(data['train_dataset_path'])
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de treinamento enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
            self.classes = current_class
            is_valid_directory, current_class, number_of_valid_images_per_class = self.__is_valid_directory_structure(data['valid_dataset_path'])
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de validação enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
            if current_class != self.classes:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Os arquivos de treinamento e validação não possuem as mesmas classes"
                )
                
            self.__copy_directory(data['train_dataset_path'], self.TRAINING_DIR)
            self.__copy_directory(data['valid_dataset_path'], self.TEST_DIR)
        
        elif self.dataset_config_mode == 'manual-config':
            if not data['file_training_images']:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Necessário que seja realizado a criação de classes para o treinamento"
                )
            
            self.classes = list(set(file.filename.split('/')[0] for file in data['file_training_images']))
            training_files, validation_files = self.split_files(data['file_training_images'])


            self.__save_images(training_files, 'train')
            self.__save_images(validation_files, 'test')
            
            is_valid_directory, current_class, number_of_train_images_per_class = self.__is_valid_directory_structure(self.TRAINING_DIR)
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de treinamento enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
            self.classes = current_class
            is_valid_directory, current_class, number_of_valid_images_per_class = self.__is_valid_directory_structure(self.TEST_DIR)
            
            if not is_valid_directory:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"O dataset de validação enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
                )
                
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Este Modo de configuração não é valido"
            )
        
        self.ready_parameters = True
        self.number_of_file_per_class = {}
        for current_class in self.classes:
            self.number_of_file_per_class[current_class] = {}
            self.number_of_file_per_class[current_class]['treinamento'] = number_of_train_images_per_class[current_class]
            self.number_of_file_per_class[current_class]['validação'] = number_of_valid_images_per_class[current_class]

    # Divisão dos arquivos em 80% para treino e 20% para teste
    def split_files(self, file_list, train_ratio=0.8):
         # Agrupar as imagens por classe
        class_groups = defaultdict(list)
        for file in file_list:
            class_name, _ = file.filename.split('/', 1)  # Separar o nome da classe do resto do caminho
            class_groups[class_name].append(file)

        train_files = []
        test_files = []

        # Para cada classe, dividir os arquivos
        for class_name, files in class_groups.items():
            random.shuffle(files)  # Embaralhar os arquivos da classe
            split_index = int(len(files) * train_ratio)  # Calcular índice de divisão
            train_files.extend(files[:split_index])  # Adicionar arquivos de treino
            test_files.extend(files[split_index:])  # Adicionar arquivos de teste

        return train_files, test_files
    
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
        generate_text_model_to_llm_in_file(3)
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
        generate_text_model_to_llm_in_file(4)
        
        
    def predict(self, image) -> dict | None:
        """
        Realiza a predição da classe para uma determinada imagem importada pelo usuário
        
        Retorno:
            Dicionário contendo classe da imagem importada ou None caso o modelo ainda não tenha sido treinado
        """
        try:
            model = self.model_used.get_loaded_model()
            processed_image = self.__load_and_process_image(image.file)
            predictions = model.predict(processed_image)
            predicted_class = np.argmax(predictions[0])
            
            classes = self.get_classes()
            probabilities = {classes[i]: f"{prob*100:.2f}%" for i, prob in enumerate(predictions[0])}
            
            return {
                "predicted_class": classes[int(predicted_class)],
                "class_probabilities": probabilities
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ocorreu um erro ao realizar a predição da image. Causa: {e}",
            )
    

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
        
        # Verifica se o diretório de destino já existe
        if os.path.exists(extract_dir):
            print(f"Diretório de destino '{extract_dir}' já existe. Removendo...")
            shutil.rmtree(extract_dir)  # Remove o diretório destino, se já existir
        
        os.makedirs(extract_dir, exist_ok=True)

        # Descompacta o arquivo zip
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        is_valid_directory, classes, numberOfImages = self.__is_valid_directory_structure(extract_dir)

        if not is_valid_directory:
            mode = "treinamento" if prefix_path == 'train' else "teste"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O dataset de {mode} enviado não é um arquivo válido. Certifque-se que o dataset possui uma arquitetura de pastas correta."
            )
        
        # Remove o arquivo zip temporário
        os.remove(temp_zip_path)
        return classes, numberOfImages
    
    def __save_images(self, file_training_images, prefix_path: str):
        saved_files = []  # Lista para armazenar os caminhos dos arquivos salvos

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        UPLOAD_DIR = os.path.join(BASE_DIR, f"../ui/statics/images/training_files/{prefix_path}")
        
        # Verifica se o diretório já existe
        if os.path.exists(UPLOAD_DIR):
            print(f"Diretório '{UPLOAD_DIR}' já existe. Removendo...")
            shutil.rmtree(UPLOAD_DIR)  # Remove o diretório destino, se já existir
            
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        for image in file_training_images:
            # Extrai o nome da classe e o nome da imagem
            class_name, image_name = os.path.split(image.filename)

            # Cria o subdiretório da classe (se não existir)
            class_dir = os.path.join(UPLOAD_DIR, class_name)
            os.makedirs(class_dir, exist_ok=True)

            # Caminho completo onde o arquivo será salvo
            file_path = os.path.join(class_dir, image_name)

            # Salva o conteúdo do arquivo de forma síncrona
            with open(file_path, "wb") as f:
                f.write(image.file.read())  # Ler e salvar o arquivo

            # Adiciona o caminho do arquivo salvo à lista
            saved_files.append(file_path)
    
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
        number_of_imges_per_class = {}
        for root, dirs, files in os.walk(base_dir):
            # Certifique-se de que existem subdiretórios no     diretório base
            if root == base_dir and not dirs:
                return False, [], {}
            
            # Certifique-se de que cada subdiretório contém imagens
            for dir_name in dirs:
                classes.append(dir_name)
                dir_path = os.path.join(root, dir_name)
                number_of_imges_per_class[dir_name] = len(os.listdir(dir_path))
                if not any(file.lower().endswith(('.png', '.jpg', '.jpeg')) for file in os.listdir(dir_path)):
                    return False, [], {}
        return True, classes, number_of_imges_per_class