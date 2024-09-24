from models.available_models.sequential_keras import SequentialKeras
from models.available_models.xception import XCeption

name_to_model = {
    'image_classification': SequentialKeras,
    'XCeption': XCeption,
    'VGG19': SequentialKeras,
    'ResNet50': SequentialKeras,
    'MobileNet': SequentialKeras,
    'InceptionV3': SequentialKeras
}