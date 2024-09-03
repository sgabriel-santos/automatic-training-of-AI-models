from abc import ABC, abstractmethod

class ImageClassification(ABC):
    
    @abstractmethod
    def fit_model(self) -> None:
        """
        Responsável por realizar o treinamento do modelo
        """
        pass
    
    @abstractmethod
    def predict(self, image) -> dict:
        """
        Função responsável por realizar a predição da classe para uma determinada imagem
        importada pelo usuário
        """
        pass
    
    @abstractmethod
    def set_parameters_to_training_model(self) -> None:
        """
        Função responsável por atualizar os parâmetros de treinamento do modelo 
        de acordo com o passado pelo usuário
        """
        pass
    
