from models.available_models.sequential_keras import SequentialKerasModel
from models.available_models.xception import XCeptionModel
from models.available_models.mobile_net import MobileNetModel
from models.available_models.resnet50 import Resnet50Model
from models.available_models.vgg19 import VGG19Model
from models.available_models.inceptionv3 import InceptionV3Model

name_to_model = {
    'image_classification': SequentialKerasModel,
    'XCeption': XCeptionModel,
    'VGG19': VGG19Model,
    'ResNet50': Resnet50Model,
    'MobileNet': MobileNetModel,
    'InceptionV3': InceptionV3Model
}