from abc import ABC, abstractmethod
from models.available_models.training_info_model import TrainingInfo
import matplotlib.pyplot as plt
import itertools
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tf_keras.models import load_model
from tf_keras.preprocessing.image import ImageDataGenerator
import json

class ImageClassification(ABC):
    directory_to_save_image = 'ui/statics/images/'
    directory_to_save_classes = 'models/results/classes.txt'
    directory_to_save_metrics = 'models/results/metrics.txt'
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
    
    def __init__(self):
        pass
    
    def save_classes(self, classes: list[str]) -> None:
        with open(self.directory_to_save_classes, 'w') as file:
            file.write(f'{classes}')
            
    def get_classes(self) -> list[str]:
        with open(self.directory_to_save_classes, 'r') as file:
            line = file.readline().replace("'", '"')
            return json.loads(line)
            
    def save_metrics(self, val_loss, val_accuracy, test_loss, test_accuracy) -> None:
        with open(self.directory_to_save_metrics, 'w') as file:
            file.write(f'{val_loss:.3f} {val_accuracy:.3f} {test_loss:.3f} {test_accuracy:.3f}')
            
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
        
        print('Saving model metrics')
        self.save_metrics(val_loss, val_accuracy, test_loss, test_accuracy)
        self.save_training_validation_loss_and_accuracy_graph(history)
        self.save_confusion_matrix_graph(test_generator, y_pred, target_names, normalize=False)
        print('Model training completed successfully')
            
    def save_training_validation_loss_and_accuracy_graph(self, history):
        history_dict = history.history
        loss_values = history_dict['loss']
        val_loss_values = history_dict['val_loss']

        epochs_x = range(1, len(loss_values) + 1)
        plt.figure(figsize=(10,10))
        plt.subplot(2,1,1)
        plt.plot(epochs_x, loss_values, 'bo', label='Training loss')
        plt.plot(epochs_x, val_loss_values, 'b', label='Validation loss')
        plt.title('Training and validation Loss and Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.subplot(2,1,2)
        acc_values = history_dict['accuracy']
        val_acc_values = history_dict['val_accuracy']
        plt.plot(epochs_x, acc_values, 'bo', label='Training acc')
        plt.plot(epochs_x, val_acc_values, 'b', label='Validation acc')
        #plt.title('Training and validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Acc')
        plt.legend()
        plt.savefig(f'{self.directory_to_save_image}Training and validation Loss and Accuracy.png')
        
    def save_confusion_matrix_graph(
        self, 
        test_generator, 
        y_pred, 
        classes, 
        normalize=True, 
        title='Confusion matrix', 
        cmap=plt.cm.Blues
    ):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        
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
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.savefig(f'{self.directory_to_save_image}confusion_matrix.png')
            
    @abstractmethod
    def fit_model(self, training_info: TrainingInfo) -> None:
        """
        Responsável por realizar o treinamento do modelo
        """
        pass
    
    
