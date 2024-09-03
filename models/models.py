from models.sequential_keras import SequentialKeras

name_to_model = {
    'image_classification': SequentialKeras,
    'XCeption': SequentialKeras,
    'VGG19': SequentialKeras,
    'ResNet50': SequentialKeras,
    'MobileNet': SequentialKeras,
    'InceptionV3': SequentialKeras
}