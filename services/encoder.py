from sentence_transformers import SentenceTransformer
from decouple import config

ENCODER_MODEL_NAME = config('ENCODER_MODEL_NAME')
DEVICE = config('DEVICE')

class Encoder:
    encoder: SentenceTransformer

    def __init__(self, model_name: str = ENCODER_MODEL_NAME, device: str = DEVICE):
        super().__init__()
        self.encoder = SentenceTransformer(model_name, device=device)
        
    def encode(self, prompt: str):
        return self.encoder.encode(prompt).tolist()
