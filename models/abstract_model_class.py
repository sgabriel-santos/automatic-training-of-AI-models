from abc import ABC, abstractmethod
import numpy as np
from sklearn.metrics import classification_report
from tf_keras.models import load_model
from tf_keras.preprocessing.image import ImageDataGenerator
from models.save_files_class import SaveFiles

class ImageClassification(ABC, SaveFiles):
    TRAINING_DIR='/home/sgabriel_santos/TCC/automatic-training-of-AI-models/training_files/train'
    TEST_DIR='/home/sgabriel_santos/TCC/automatic-training-of-AI-models/training_files/test'
    MODEL_NAME_RESULT = 'models/results/image_classification.model.keras'
    
    epochs = 1
    shuffle = True
    seed = 10
    batch_size = 10
    im_shape = (250,250)
    
    train_generator = None
    validation_generator = None
    test_generator = None
    
    def __init__(self): pass
    
    def set_parameters_to_training_model(self, data):
        self.model_name = data['model_name']
        self.epochs = data['epochs']
        self.shuffle = data['shuffle']
        self.seed = data['seed']
        self.batch_size = data['batch_size']
            
    def get_or_build_train_generator(self):
        # Generator para parte train
        if self.train_generator: return self.train_generator
        data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)
        train_generator = data_generator.flow_from_directory(
            self.TRAINING_DIR, 
            target_size=self.im_shape, 
            shuffle=self.shuffle, 
            seed=self.seed,
            class_mode='categorical', 
            batch_size=self.batch_size, 
            subset="training"
        )
        self.train_generator = train_generator
        return train_generator
    
    def get_or_build_validation_generator(self):
        # Generator para parte validação
        if self.validation_generator: return self.validation_generator
        val_data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)
        validation_generator = val_data_generator.flow_from_directory(
            self.TRAINING_DIR, 
            target_size=self.im_shape, 
            shuffle=False, 
            seed=self.seed,
            class_mode='categorical', 
            batch_size=self.batch_size, 
            subset="validation"
        )
        self.validation_generator = validation_generator
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
            
    def test_model(self, history):
        print('Iniciando carregamento do modelo para validações')
        model = load_model(self.MODEL_NAME_RESULT)

        # Using the validation dataset
        validation_score = model.evaluate(self.get_or_build_validation_generator())
        val_loss, val_accuracy = validation_score[0], validation_score[1]
        print('Val loss:', val_loss)
        print('Val accuracy:', val_accuracy)

        # Using the test dataset
        test_generator = self.get_or_build_test_generator()
        test_score_score = model.evaluate(test_generator)
        test_loss, test_accuracy = test_score_score[0], test_score_score[1]
        print('Test loss:', test_loss)
        print('Test accuracy:', test_accuracy)

        #On test dataset
        Y_pred = model.predict(test_generator)
        y_pred = np.argmax(Y_pred, axis=1)
        target_names = self.get_classes()

        #Classification Report
        print('Classification Report')
        print(classification_report(test_generator.classes, y_pred, target_names=target_names))
        
        self.save_metrics(val_loss, val_accuracy, test_loss, test_accuracy)
        self.save_training_validation_loss_and_accuracy_graph(history)
        self.save_confusion_matrix_graph(test_generator, y_pred, target_names, normalize=False)
        print('Model training completed successfully')
            
    @abstractmethod
    def fit_model(self) -> None:
        """
        Responsável por realizar o treinamento do modelo
        """
        pass
    
    
