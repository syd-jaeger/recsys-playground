from src.models.base import BaseRecommender

class LLMRecommender(BaseRecommender):
    """
    A stub for a future LLM-based recommender system as shown in AIRecoSystem_LLM.ipynb.
    This class can be expanded later to integrate with transformers/LLMs.
    """
    def __init__(self, model_name="EleutherAI/gpt-neo-1.3B"):
        self.model_name = model_name
        self.is_fitted = False

    def fit(self, data):
        # In a real implementation, you might build a context catalog here.
        self.is_fitted = True
        pass

    def recommend(self, user_id, n=5):
        if not self.is_fitted:
             raise ValueError("Model is not fitted yet. Call fit(data) first.")

        # Stub logic
        return [
            {'title': f'LLM Generated Movie {i}', 'score': 0.99 - (i * 0.05)}
            for i in range(1, n + 1)
        ]
