from abc import ABC, abstractmethod
import numpy as np
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
from tf_keras.callbacks import History
from tf_keras.models import load_model, Model
from tf_keras.preprocessing.image import ImageDataGenerator
from autotrain_with_llm.models.save_files_class import SaveFiles
import math
import os

class ImageClassification(ABC, SaveFiles):
    TRAINING_DIR=None
    TEST_DIR=None
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_NAME_RESULT = os.path.join(BASE_DIR, "results/image_classification.model.keras")
    
    epochs = 1
    shuffle = True
    seed = 10
    batch_size = 10
    im_shape = (250,250)
    
    is_absolute_path = None
    
    train_generator = None
    validation_generator = None
    test_generator = None
    
    val_loss = val_accuracy = None
    test_loss = test_accuracy = None
    precision = recall = f1 = None
    
    confusion_matrix_values = None
    model_loaded = None

    
    def __init__(self): pass
    
    def set_parameters_to_training_model(self, data):
        self.model_name = data['model_name']
        self.epochs = data['epochs']
        self.shuffle = data['shuffle']
        self.seed = data['seed']
        self.batch_size = data['batch_size']
        self.TRAINING_DIR = os.path.join(self.BASE_DIR, "../ui/statics/images/training_files/train")
        self.TEST_DIR = os.path.join(self.BASE_DIR, "../ui/statics/images/training_files/test")
        
        self.dataset_config_mode = data['dataset_config_mode']
        if self.dataset_config_mode == 'dataset-path':
            self.TRAINING_DIR = data['train_dataset_path']
            self.TEST_DIR = data['valid_dataset_path']
            
    def get_or_build_train_generator(self):
        # Generator para parte train
        if self.train_generator: return self.train_generator
        data_generator = ImageDataGenerator(rescale=1./250)
        train_generator = data_generator.flow_from_directory(
            self.TRAINING_DIR, 
            target_size=self.im_shape, 
            shuffle=self.shuffle, 
            seed=self.seed,
            class_mode='categorical', 
            batch_size=self.batch_size, 
        )
        self.train_generator = train_generator
        print(f'Quantidade de imagens para treinamento: {train_generator.samples}')
        return train_generator
    
    def get_or_build_validation_generator(self):
        # Generator para parte validação
        if self.validation_generator: return self.validation_generator
        val_data_generator = ImageDataGenerator(rescale=1./250)
        validation_generator = val_data_generator.flow_from_directory(
            self.TEST_DIR, 
            target_size=self.im_shape, 
            shuffle=False, 
            seed=self.seed,
            class_mode='categorical', 
            batch_size=self.batch_size, 
        )
        self.validation_generator = validation_generator
        print(f'Quantidade de imagens para validação: {validation_generator.samples}')
        return validation_generator
    
    def get_or_build_test_generator(self):
        # Generator para dataset de teste
        if self.test_generator: return self.test_generator
        test_generator = ImageDataGenerator(rescale=1./250)
        test_generator = test_generator.flow_from_directory(
            self.TEST_DIR, 
            target_size=self.im_shape, 
            shuffle=False, 
            seed=self.seed,
            class_mode='categorical', 
            batch_size=self.batch_size
        )
        self.test_generator = test_generator
        return test_generator
    
    def get_classes(self):
        train_generator = self.get_or_build_train_generator()
        classes = list(train_generator.class_indices.keys())
        print(f'Classes: {str(classes)}')
        self.classes = classes
        self.save_classes(classes)
        return classes
    
    def get_loaded_model(self):
        if self.model_loaded: return self.model_loaded
        else:
            self.model_loaded = load_model(self.MODEL_NAME_RESULT)
            return self.model_loaded
                
    def test_model(self, history: History):
        print('Iniciando carregamento do modelo para validações')
        model = self.get_loaded_model()
        print('Modelo carregado')

        # Using the validation dataset
        validation_score = model.evaluate(self.get_or_build_validation_generator())
        self.val_loss, self.val_accuracy = validation_score[0], validation_score[1]
        print('Val loss:', self.val_loss)
        print('Val accuracy:', self.val_accuracy)

        # Using the test dataset
        test_generator = self.get_or_build_test_generator()
        test_score_score = model.evaluate(test_generator)
        self.test_loss, self.test_accuracy = test_score_score[0], test_score_score[1]
        print('Test loss:', self.test_loss)
        print('Test accuracy:', self.test_accuracy)

        #On test dataset
        Y_pred = model.predict(test_generator)
        y_pred = np.argmax(Y_pred, axis=1)
        target_names = self.get_classes()
        
        # Precisão, Revocação e F1-Score
        self.precision = precision_score(test_generator.classes, y_pred, average='weighted')
        self.recall = recall_score(test_generator.classes, y_pred, average='weighted')
        self.f1 = f1_score(test_generator.classes, y_pred, average='weighted')

        print(f"Precisão (Precision): {self.precision * 100:.2f}%")
        print(f"Revocação (Recall): {self.recall * 100:.2f}%")
        print(f"F1-Score: {self.f1 * 100:.2f}%")

        #Classification Report
        print('Classification Report')
        print(classification_report(test_generator.classes, y_pred, target_names=target_names))
        
        self.save_metrics(self.val_loss, self.val_accuracy, self.test_loss, self.test_accuracy)
        self.save_training_validation_loss_and_accuracy_graph(history)
        self.confusion_matrix_values = self.save_confusion_matrix_graph(test_generator, y_pred, target_names, normalize=False)
        print('Model training completed successfully')
        
    def fit_and_save_model(self, model: Model) -> History:
        print('Iniciando treinamento do modelo')
        
        train_generator = self.get_or_build_train_generator()
        validation_generator = self.get_or_build_validation_generator()
        nb_train_samples = train_generator.samples
        nb_validation_samples = validation_generator.samples
        
        #Training        
        history = model.fit(
            self.train_generator,
            steps_per_epoch=math.ceil(nb_train_samples / self.batch_size),
            epochs=self.epochs,
            validation_data=validation_generator,
            verbose = 1,
            validation_steps=math.ceil(nb_validation_samples / self.batch_size)
        )
        
        print('Salvando Modelo')
        try:
            os.makedirs(os.path.dirname(self.MODEL_NAME_RESULT), exist_ok=True)
            model.save(self.MODEL_NAME_RESULT)
            print('Modelo Salvo com sucesso')
        except:
            print('Erro ao salvar o modelo. Isso impedirá que o download seja feita nas etapas seguintes')
        
        self.model_loaded = model
        return history
        
            
    @abstractmethod
    def fit_model(self) -> History:
        """
        Responsável por realizar o treinamento do modelo
        """
        pass
    
    
