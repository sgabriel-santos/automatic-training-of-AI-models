from tf_keras.callbacks import EarlyStopping, ModelCheckpoint
from tf_keras.preprocessing.image import ImageDataGenerator
from tf_keras.models import Sequential, load_model
from tf_keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tf_keras.optimizers import Adam
from sklearn.metrics import classification_report
from models.abstract_model_class import ImageClassification
from models.available_models.training_info_model import TrainingInfo
import numpy as np
import os

def exists_directory(directory: str):
    if not os.path.isdir(directory):
        print(f'{directory} directory does not exist')
        return False
    return True

class SequentialKeras(ImageClassification):
    
    def __init__(self):
        pass

    def fit_model(
        self,
        training_info: TrainingInfo,
    ) -> None:
        if(not exists_directory(training_info.TRAINING_DIR)): return False
        if(not exists_directory(training_info.TEST_DIR)): return False

        # Using keras ImageGenerator and flow_from_directoty
        # Subdivision in test/validation
        train_generator = self.get_or_build_train_generator()
        validation_generator = self.get_or_build_validation_generator()
        test_generator = self.get_or_build_test_generator()

        nb_train_samples = train_generator.samples
        nb_validation_samples = validation_generator.samples
        classes = list(train_generator.class_indices.keys())
        print(f'Classes: {str(classes)}')
        num_classes  = len(classes)
        self.classes = classes
        self.save_classes(classes)
        
        model = Sequential()
        model.add(Conv2D(80, kernel_size=(3, 3),
                        activation='relu',
                        input_shape=(training_info.im_shape[0], training_info.im_shape[1],3)))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(50, kernel_size=(3,3), activation='relu'))

        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(100, kernel_size=(3,3), activation='relu'))

        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(80, kernel_size=(3,3), activation='relu'))

        model.add(Flatten())

        model.add(Dense(120, activation='relu'))

        model.add(Dropout(0.2))
        model.add(Dense(num_classes, activation='softmax'))
        model.summary()


        # Compila o modelo
        model.compile(loss='categorical_crossentropy',
                    optimizer=Adam(learning_rate=0.002),
                    metrics=['accuracy'])

        print(f'Quantidade de épocas para treinamento: {training_info.epochs}')

        #Callback to save the best model
        callbacks_list = [
            ModelCheckpoint(
                filepath=training_info.MODEL_NAME_RESULT,
                monitor='val_loss', save_best_only=True, verbose=1
            ),
            EarlyStopping(monitor='val_loss', patience=10,verbose=1)
        ]

        print('Iniciando treinamento do modelo')
        #Training
        history = model.fit(
                train_generator,
                # steps_per_epoch=nb_train_samples // training_info.batch_size,
                steps_per_epoch=10,
                epochs=training_info.epochs,
                callbacks = callbacks_list,
                validation_data=validation_generator,
                verbose = 1,
                validation_steps=nb_validation_samples // training_info.batch_size)
        return history