import pandas as pd
from abc import ABC, abstractmethod
import os

class DatasetLoader(ABC):
    @abstractmethod
    def load_data(self):
        """Loads and returns the dataset as a DataFrame."""
        pass

    @abstractmethod
    def get_users(self):
        """Returns a list of unique user IDs."""
        pass

class MovieLensLoader(DatasetLoader):
    def __init__(self, data_path='datasets/u.data', titles_path='datasets/Movie_Id_Titles.txt'):
        self.data_path = data_path
        self.titles_path = titles_path
        self.df = None
        self._load_and_merge()

    def _load_and_merge(self):
        # Load user interactions
        column_names = ['user_id', 'item_id', 'rating', 'timestamp']
        if not os.path.exists(self.data_path) or not os.path.exists(self.titles_path):
             raise FileNotFoundError(f"Ensure {self.data_path} and {self.titles_path} exist.")

        data_df = pd.read_csv(self.data_path, sep='\t', names=column_names)

        # Load movie titles
        titles_df = pd.read_csv(self.titles_path)

        # Merge datasets
        self.df = pd.merge(data_df, titles_df, on='item_id')

    def load_data(self):
        return self.df

    def get_users(self):
        if self.df is not None:
            return self.df['user_id'].unique().tolist()
        return []

    def get_user_history(self, user_id):
        """Returns a list of highly rated movies (rating >= 4) for the given user"""
        if self.df is not None:
            user_data = self.df[(self.df['user_id'] == user_id) & (self.df['rating'] >= 4)]
            # Sort by rating descending and return top 10 movies
            user_data = user_data.sort_values(by='rating', ascending=False).head(10)
            return user_data[['item_id', 'title', 'rating']].to_dict('records')
        return []
