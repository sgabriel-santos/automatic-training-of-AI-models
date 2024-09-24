from tf_keras.models import Sequential
from tf_keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tf_keras.optimizers import Adam
from tf_keras.callbacks import History
from models.abstract_model_class import ImageClassification

class SequentialKeras(ImageClassification):
    
    def __init__(self):
        pass

    def fit_model(self) -> History:
        classes = self.get_classes()
        num_classes = len(classes)
        
        model = Sequential()
        model.add(Conv2D(80, kernel_size=(3, 3),
                        activation='relu',
                        input_shape=(self.im_shape[0], self.im_shape[1],3)))
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
        
        return self.fit_and_save_model(model)