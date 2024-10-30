from tf_keras.applications import ResNet50
from tf_keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tf_keras.models import Model
from autotrain_with_llm.models.abstract_model_class import ImageClassification
from tf_keras.callbacks import History

class Resnet50Model(ImageClassification):
    
    def __init__(self): pass

    def fit_model(self) -> History:
        classes = self.get_classes()
        
        # carrega a ResNet50 pré-treinada com os pesos do ImageNet
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(self.im_shape[0], self.im_shape[1], 3))

        # adiciona camadas adicionais para a classificação
        dropout_rate = 0.2
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        x = Dropout(dropout_rate)(x)
        predictions = Dense(len(classes), activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        return self.fit_and_save_model(model)