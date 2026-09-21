from abc import ABC, abstractmethod

class BaseRecommender(ABC):
    @abstractmethod
    def fit(self, data):
        """Fits the model using the provided data."""
        pass

    @abstractmethod
    def recommend(self, user_id, n=5):
        """Generates n recommendations for a given user."""
        pass
