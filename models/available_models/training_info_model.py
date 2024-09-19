from pydantic import BaseModel

class TrainingInfo(BaseModel):
    MODEL_NAME_RESULT: str
    TRAINING_DIR: str
    TEST_DIR: str
    epochs: int
    shuffle: bool
    seed: int
    batch_size: int
    im_shape: tuple[int, int]