from models.models import name_to_model

class Managermodel:
    _instance = None
    training_model = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.training_model = False
        return cls._instance

    def get_model(self, model_name):
        if model_name in name_to_model:
            return name_to_model[model_name]()
        return False
    
    def is_training_model(self):
        return self.training_model
    
    def update_training_model(self, is_training: bool): 
        self.training_model = is_training