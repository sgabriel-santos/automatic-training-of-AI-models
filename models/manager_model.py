from models.models import name_to_model
from models.abstract_model_class import ImageClassification

class Managermodel:
    _instance = None
    model_name = None
    training_model = False
    epochs = 1
    shuffle = True
    seed = 10
    batch_size = 10
    model_used: ImageClassification | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.training_model = False
        return cls._instance
    
    def set_model_to_be_used(self, model_name):
        self.model_used = self.__get_model(model_name)

    def set_parameters_to_training_model(self, data: dict):
        self.model_name = data['model_name']
        self.epochs = data['epochs']
        self.shuffle = data['shuffle']
        self.seed = data['seed']
        self.batch_size = data['batch_size']
        self.model_used.set_parameters_to_training_model(data)
    
    def is_training_model(self):
        return self.training_model
    
    def update_training_model(self, is_training: bool): 
        self.training_model = is_training
        
    def fit_model(self, generate_text_model_to_llm_in_file):
        self.update_training_model(True)
        generate_text_model_to_llm_in_file()
        self.model_used.fit_model()
        self.update_training_model(False)
        generate_text_model_to_llm_in_file()
        
    def predict(self, image) -> dict | None:
        """
        Realiza a predição da classe para uma determinada imagem importada pelo usuário
        
        Retorno:
            Dicionário contendo classe da imagem importada ou None caso o modelo ainda não tenha sido treinado
        """
        if self.model_used:
            return self.model_used.predict(image)
        return None
        
        
    def __get_model(self, model_name):
        if model_name in name_to_model:
            return name_to_model[model_name]()
        return False