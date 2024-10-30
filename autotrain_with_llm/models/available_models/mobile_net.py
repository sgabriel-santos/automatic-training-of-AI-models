
from tf_keras.layers import Dense
from tf_keras.models import Model
from tf_keras.layers import Dense,GlobalAveragePooling2D, Dropout
from tf_keras.applications.mobilenet import MobileNet
from autotrain_with_llm.models.abstract_model_class import ImageClassification
from tf_keras.callbacks import History

class MobileNetModel(ImageClassification):
    
    def __init__(self): pass

    def fit_model(self) -> History:
        classes = self.get_classes()
        
        base_model=MobileNet(weights='imagenet',include_top=False)  #imports the mobilenet model and discards the last 1000 neuron layer.

        x= base_model.output
        x= GlobalAveragePooling2D()(x)
        x= Dense(1024,activation='relu')(x)
        x= Dense(1024,activation='relu')(x)
        x= Dense(1024,activation='relu')(x)
        x= Dense(1024,activation='relu')(x)
        x= Dense(512,activation='relu')(x) 
        x = Dropout(0.2)(x)
        preds=Dense(len(classes), activation='softmax')(x)
        
        model=Model(inputs=base_model.input,outputs=preds)
        
        model.compile(optimizer='Adam',loss='categorical_crossentropy',metrics=['accuracy']) 
        
        for layer in model.layers[:20]:
            layer.trainable=False
        for layer in model.layers[20:]:
            layer.trainable=True 
        
        return self.fit_and_save_model(model)