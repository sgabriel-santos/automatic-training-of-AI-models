from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report
from PIL import Image
import numpy as np
import numpy as np
import os
from fastapi import UploadFile
import shutil
import zipfile

def exists_directory(directory: str):
    if not os.path.isdir(directory):
        print(f'{directory} directory does not exist')
        return False
    return True

class ImageClassification():
    epochs = 1
    shuffle = True
    seed = 10
    batch_size = 10
    MODEL_NAME_RESULT = 'models/results/image_classification.model.keras'
    im_shape = (250,250)
    TRAINING_DIR = '/home/sgabriel_santos/TCC/automatic-training-of-AI-models/training_files/train'
    TEST_DIR = '/home/sgabriel_santos/TCC/automatic-training-of-AI-models/training_files/test'
    classes = ['glioma', 'meningioma', 'pituitary tumor']

    def __init__(self):
        pass

    def get_parameters(self, data: dict):
        self.epochs = data['epochs']
        self.shuffle = data['shuffle']
        self.seed = data['seed']
        self.batch_size = data['batch_size']
        print(data['file_training'].filename)
        if(data['file_training'].filename): self.save_files(data['file_training'], 'train')
        if(data['file_validation'].filename): self.save_files(data['file_validation'], 'test')

    def save_files(self, file: UploadFile, prefix_path: str):
        # Verifica se o arquivo é um zip
        # if not file.filename.endswith('.zip'):
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a ZIP")

        # Define o caminho onde o zip será salvo temporariamente
        temp_zip_path = "temp.zip"
        
        # Salva o arquivo zip temporariamente
        with open(temp_zip_path, "wb") as temp_zip:
            shutil.copyfileobj(file.file, temp_zip)
        
        extract_dir = f"training_files/{prefix_path}"
        os.makedirs(extract_dir, exist_ok=True)

        # Descompacta o arquivo zip
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # if not self.is_valid_directory_structure(dataset)
        
        # Remove o arquivo zip temporário
        os.remove(temp_zip_path)

    def is_valid_directory_structure(base_dir):
        """
        Verifica se o diretório descompactado possui a estrutura correta:
        - Vários diretórios
        - Cada diretório contém múltiplas imagens
        """
        for root, dirs, files in os.walk(base_dir):
            # Certifique-se de que existem subdiretórios no diretório base
            if root == base_dir and not dirs:
                return False
            
            # Certifique-se de que cada subdiretório contém imagens
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not any(file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) for file in os.listdir(dir_path)):
                    return False

        return True


    def fit_model(self, manager_model: dict, with_try_except: bool = True):
        manager_model.update_training_model(True)
        if with_try_except:
            try:
                self.fit()
            except Exception as e:
                print('\nexcess generated during model training')
                print(f'mensage: {e}')
        else:
            self.fit()

        manager_model.update_training_model(False)

    def fit(self):
        if(not exists_directory(self.TRAINING_DIR)): return False
        if(not exists_directory(self.TEST_DIR)): return False

        data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)
        val_data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)

        #Using keras ImageGenerator and flow_from_directoty

        # Subdivision in test/validation
        data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)
        val_data_generator = ImageDataGenerator(rescale=1./250, validation_split=0.2)


        # Generator para parte train
        train_generator = data_generator.flow_from_directory(
            self.TRAINING_DIR, target_size=self.im_shape, shuffle=self.shuffle, seed=self.seed,
            class_mode='categorical', batch_size=self.batch_size, subset="training"
        )
        # Generator para parte validação
        validation_generator = val_data_generator.flow_from_directory(
            self.TRAINING_DIR, target_size=self.im_shape, shuffle=False, seed=self.seed,
            class_mode='categorical', batch_size=self.batch_size, subset="validation"
        )

        # Generator para dataset de teste\
        test_generator = ImageDataGenerator(rescale=1./250)
        test_generator = test_generator.flow_from_directory(
            self.TEST_DIR, target_size=self.im_shape, shuffle=False, seed=self.seed,
            class_mode='categorical', batch_size=self.batch_size
        )

        nb_train_samples = train_generator.samples
        nb_validation_samples = validation_generator.samples
        classes = list(train_generator.class_indices.keys())
        print('Classes: '+str(classes))
        num_classes  = len(classes)
        self.classes = classes
        
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

        print(f'Quantidade de épocas para treinamento: {self.epochs}')

        #Callback to save the best model
        callbacks_list = [
            keras.callbacks.ModelCheckpoint(
                filepath=self.MODEL_NAME_RESULT,
                monitor='val_loss', save_best_only=True, verbose=1
            ),
            keras.callbacks.EarlyStopping(monitor='val_loss', patience=10,verbose=1)
        ]

        print('Iniciando treinamento do modelo')
        #Training
        history = model.fit(
                train_generator,
                # steps_per_epoch=nb_train_samples // self.batch_size,
                steps_per_epoch=10,
                epochs=self.epochs,
                callbacks = callbacks_list,
                validation_data=validation_generator,
                verbose = 1,
                validation_steps=nb_validation_samples // self.batch_size)
        
        print('Modelo Treinado com suceso')
        print('Iniciando carregamento do modelo para validações')
        model = load_model(self.MODEL_NAME_RESULT)

        # Using the validation dataset
        score = model.evaluate(validation_generator)
        print('Val loss:', score[0])
        print('Val accuracy:', score[1])

        # Using the test dataset
        score = model.evaluate(test_generator)
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])

        #On test dataset
        Y_pred = model.predict(test_generator)
        y_pred = np.argmax(Y_pred, axis=1)
        target_names = classes

        #Classification Report
        print('Classification Report')
        print(classification_report(test_generator.classes, y_pred, target_names=target_names))

    def load_and_process_image(self, img):
        img = Image.open(img)
        
        if img.mode != 'RGB': img = img.convert('RGB')
        
        img = img.resize(self.im_shape)
        img_array = np.array(img)
        img_array = img_array / 255.0  # Normalização
        img_array = np.expand_dims(img_array, axis=0)  # Adicionar dimensão do batch
        return img_array
    
    def predict(self, image):
        from tensorflow.keras.models import load_model
        import numpy as np
        model = load_model(self.MODEL_NAME_RESULT)
        processed_image = self.load_and_process_image(image.file)
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])

        return {"predicted_class": self.classes[int(predicted_class)]}