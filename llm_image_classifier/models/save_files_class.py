import os
import json
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import numpy as np
import itertools

class SaveFiles():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(BASE_DIR, "results/image_classification.model.keras")
    directory_to_save_image = os.path.join(BASE_DIR, "../ui/statics/images/")
    directory_to_save_classes = os.path.join(BASE_DIR, "results/classes.txt")
    directory_to_save_metrics = os.path.join(BASE_DIR, "results/metrics.txt")
    MODEL_NAME_RESULT = os.path.join(BASE_DIR, "results/image_classification.model.keras")
    
    def __init__(self): pass
    
    def save_classes(self, classes: list[str]) -> None:
        try:
            print('Salvando clases coletadas')
            os.makedirs(os.path.dirname(self.directory_to_save_classes), exist_ok=True)
            with open(self.directory_to_save_classes, 'w') as file:
                file.write(f'{classes}')
            return True
        except FileNotFoundError:
            print(f'Erro: O diretório ou arquivo {self.directory_to_save_classes} não foi encontrado.')
            raise FileNotFoundError(f'Arquivo {self.directory_to_save_classes} não encontrado.')
        except OSError as e:
            print(f'Erro de sistema ao acessar o arquivo: {e}')
            raise OSError(f'Falha ao salvar as classes: {e}')
        except Exception as e:
            print(f'Erro inesperado: {e}')
            raise Exception('Erro inesperado ao salvar as classes.')
        
    def get_classes(self) -> list[str]:
        print('Buscando Classes')
        with open(self.directory_to_save_classes, 'r') as file:
            line = file.readline().replace("'", '"')
            return json.loads(line)
     
     
    def save_metrics(self, val_loss, val_accuracy, test_loss, test_accuracy) -> None:
        try:
            print('Salvando Métricas')
            os.makedirs(os.path.dirname(self.directory_to_save_metrics), exist_ok=True)
            with open(self.directory_to_save_metrics, 'w') as file:
                file.write(f'{val_loss} {val_accuracy} {test_loss} {test_accuracy}')
            print('Métricas salvas')
        except FileNotFoundError:
            print(f'Erro: O diretório ou arquivo {self.directory_to_save_metrics} não foi encontrado.')
            raise FileNotFoundError(f'Arquivo {self.directory_to_save_metrics} não encontrado.')
        except OSError as e:
            print(f'Erro de sistema ao acessar o arquivo: {e}')
            raise OSError(f'Falha ao salvar as classes: {e}')
        except Exception as e:
            print(f'Erro inesperado: {e}')
            raise Exception('Erro inesperado ao salvar as classes.')

    def get_metrics(self) -> list[str]:
        try:
            print('Buscando Métricas')
            with open(self.directory_to_save_metrics, 'r') as file:
                vl, va, tl, ta = file.readline().split(' ')
                return [vl, va, tl, ta]
        except:
            print('Erro ao coletar informações de métricas do modelo treinado')
            return []
            
    
    def save_training_validation_loss_and_accuracy_graph(self, history) -> bool:
        try:    
            history_dict = history.history
            loss_values = history_dict['loss']
            val_loss_values = history_dict['val_loss']

            epochs_x = range(1, len(loss_values) + 1)
            plt.figure(figsize=(10,10))
            plt.subplot(2,1,1)
            plt.plot(epochs_x, loss_values, 'bo', label='Training loss')
            plt.plot(epochs_x, val_loss_values, 'b', label='Validation loss')
            plt.title('Gráfico de perda e Acurácia')
            plt.xlabel('Épocas')
            plt.ylabel('Perda')
            plt.legend()
            plt.subplot(2,1,2)
            acc_values = history_dict['accuracy']
            val_acc_values = history_dict['val_accuracy']
            plt.plot(epochs_x, acc_values, 'bo', label='Training acc')
            plt.plot(epochs_x, val_acc_values, 'b', label='Validation acc')
            #plt.title('Training and validation accuracy')
            plt.xlabel('Épocas')
            plt.ylabel('Acurácia')
            plt.legend()
            os.makedirs(os.path.dirname(self.directory_to_save_image), exist_ok=True)
            plt.savefig(f'{self.directory_to_save_image}Training and validation Loss and Accuracy.png', dpi=300, bbox_inches='tight')
            print('Informações de validações do modelo salvas com sucesso')
            return True
        except Exception as e:
            print('Erro ao salvar informações de validação do modelo')
            print(f'Error: {e}')
            return False
        
    
    def save_confusion_matrix_graph(
        self, 
        test_generator, 
        y_pred, 
        classes, 
        normalize=True, 
        title='Matriz de Confusão', 
        cmap=plt.cm.Blues
    ) -> bool:
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        
        try:
            cm = confusion_matrix(test_generator.classes, y_pred)
            plt.figure(figsize=(10,10))
            plt.imshow(cm, interpolation='nearest', cmap=cmap)
            plt.title(title)
            plt.colorbar()
            tick_marks = np.arange(len(classes))
            plt.xticks(tick_marks, classes, rotation=45)
            plt.yticks(tick_marks, classes)
            if normalize:
                cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
                cm = np.around(cm, decimals=2)
                cm[np.isnan(cm)] = 0.0
            thresh = cm.max() / 2.
            for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
                plt.text(j, i, cm[i, j],
                        horizontalalignment="center",
                        color="white" if cm[i, j] > thresh else "black")
            
            plt.tight_layout(pad=2.0)  # Define um padding adicional para evitar cortes
            plt.ylabel('Classe Verdadeira', fontsize=12)  # Aumenta o tamanho da fonte para visibilidade
            plt.xlabel('Classe Prevista', fontsize=12)
            os.makedirs(os.path.dirname(self.directory_to_save_image), exist_ok=True)
            plt.savefig(f'{self.directory_to_save_image}confusion_matrix.png', dpi=300, bbox_inches='tight')
            print('Matriz confusão salva com sucesso')
            return cm.ravel()
        except Exception as e:
            print('Erro ao salvar matriz confusão')
            print(f'Error: {e}')
            return False