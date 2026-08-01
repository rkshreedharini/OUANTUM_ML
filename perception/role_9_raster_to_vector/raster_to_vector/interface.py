import numpy as np
from .classical import ClassicalVectorizer
from .learned import LearnedVectorizer

class Vectorizer:
    def __init__(self, style="manhattan", learned_model_path=None, device="cpu"):
        self.style = style.lower()
        if self.style == "manhattan" or self.style == "classical":
            self.backend = ClassicalVectorizer()
        elif self.style == "irregular" or self.style == "learned":
            self.backend = LearnedVectorizer(model_path=learned_model_path, device=device)
        else:
            raise ValueError(f"Unknown style '{style}'. Choose 'manhattan' or 'irregular'.")
            
    def process(self, mask: np.ndarray) -> list:
        return self.backend.vectorize(mask)
