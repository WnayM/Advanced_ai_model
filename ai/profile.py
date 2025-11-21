from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class UserProgileCongig:
    use_dislikes: bool = True
    min_likes = 1

class UserProfileBuilder:
    def __init__(self, config: Optional[UserProgileCongig] = None) -> None:
        self.config = config or UserProgileCongig()

    def build(self, liked_embenddings: np.ndarray, disliked_embeddings: Optional[np.ndarray] = None) -> np.ndarray:
        if liked_embenddings.size == 0 or liked_embenddings.shape[0] < self.config.min_likes:
            raise ValueError(
                f"Недостаточно лайкнутых новостей (минимум {self.config.min_likes})."
            )
        
        user_vec = liked_embenddings.mean(axis = 0)

        if(self.config.use_dislikes
            and disliked_embeddings is not None
            and disliked_embeddings.size > 0):

            dislike_vec = disliked_embeddings.mean(axis=0)
            user_vec = user_vec - dislike_vec

        norm = np.linalg.norm(user_vec)
        if norm > 0:
            user_vec = user_vec / norm

        return user_vec