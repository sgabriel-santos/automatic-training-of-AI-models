from tf_keras.applications.vgg19 import VGG19
from tf_keras.layers import Dense, GlobalAveragePooling2D
from tf_keras import layers, Input, applications, Sequential, Model
from autotrain_with_llm.models.abstract_model_class import ImageClassification
from tf_keras.callbacks import History

class VGG19Model(ImageClassification):
    
    def __init__(self): pass

    def fit_model(self) -> History:
        classes = self.get_classes()
        
        data_augmentation = Sequential([
            layers.RandomFlip('horizontal'),
            layers.RandomRotation(0.2),
        ])
        
        preprocess_input = applications.vgg19.preprocess_input
        base_model = VGG19(input_shape=(self.im_shape[0], self.im_shape[1],3),
                            include_top=False,
                            weights='imagenet')
        base_model.summary()
        
        global_average_layer = GlobalAveragePooling2D()
        prediction_layer = Dense(len(classes))
        
        inputs = Input(shape=(self.im_shape[0], self.im_shape[1], 3))
        x = data_augmentation(inputs)
        x = preprocess_input(x)
        x = base_model(x, training=False)
        x = global_average_layer(x)
        x = layers.Dropout(0.2)(x)
        outputs = prediction_layer(x)
        model = Model(inputs, outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        return self.fit_and_save_model(model)