from tf_keras.applications.xception import Xception
from tf_keras.layers import Dense, GlobalAveragePooling2D
from tf_keras.callbacks import History
from tf_keras.models import Model
from tf_keras.optimizers import RMSprop
from autotrain_with_llm.models.abstract_model_class import ImageClassification

class XCeptionModel(ImageClassification):
    
    def __init__(self): pass

    def fit_model(self) -> History:
        classes = self.get_classes()
        
        # Dimensões das imagens de entrada
        img_width, img_height = self.im_shape
        input_shape = (img_width, img_height, 3)
        
        # Hiperparâmetros de treinamento
        learning_rate = 0.001
        
        print('Hiperparâmetros definidos')
        
        # Criar o modelo base utilizando a arquitetura Xception (sem as camadas fully-connected)
        print('Criando modelo na arquitetura Xception')
        base_model = Xception(weights='imagenet', include_top=False, input_shape=input_shape)
        
        # Congelar os pesos das camadas do modelo base para evitar o treinamento
        for layer in base_model.layers:
            layer.trainable = False
            
        # Adicionar camadas fully-connected no topo do modelo base
        print('Adicionando camadas fully-connected')
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu')(x)
        predictions = Dense(len(classes), activation='softmax')(x)
        
        # Definir o modelo final
        print('Definindo modelo final')
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compilar o modelo com otimizador RMSProp
        print('Compilando modelo com otimizador RMSProp')
        optimizer = RMSprop(learning_rate=learning_rate)
        model.compile(optimizer=optimizer,
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])
        
        return self.fit_and_save_model(model)