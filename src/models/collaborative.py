import pandas as pd
import numpy as np
from src.models.base import BaseRecommender

class ItemBasedCFRecommender(BaseRecommender):
    def __init__(self, min_ratings=100):
        self.min_ratings = min_ratings
        self.moviemat = None
        self.ratings = None

    def fit(self, data):
        """
        Fits the recommender on the DataFrame `data` which has
        'user_id', 'title', and 'rating' columns.
        """
        # Create user-item interaction matrix
        self.moviemat = data.pivot_table(index='user_id', columns='title', values='rating')

        # Calculate rating statistics
        self.ratings = pd.DataFrame(data.groupby('title')['rating'].mean())
        self.ratings['num of ratings'] = pd.DataFrame(data.groupby('title')['rating'].count())

    def recommend(self, user_id, n=5):
        """
        Recommends `n` movies for `user_id` based on correlation with their highly rated movies.
        """
        if self.moviemat is None or self.ratings is None:
            raise ValueError("Model is not fitted yet. Call fit(data) first.")

        if user_id not in self.moviemat.index:
            return [] # Unknown user

        # Get user's ratings
        user_ratings = self.moviemat.loc[user_id].dropna()
        if user_ratings.empty:
            return []

        # Consider top rated movies by user to find similar ones
        top_user_movies = user_ratings[user_ratings >= 4.0].index.tolist()
        # If user has no highly rated movies, just use what they have
        if not top_user_movies:
            top_user_movies = user_ratings.index.tolist()

        recommendations = pd.Series(dtype=float)

        import warnings
        for movie in top_user_movies:
            movie_ratings = self.moviemat[movie]
            # Suppress RuntimeWarnings for division by zero in correlation
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                similar_movies = self.moviemat.corrwith(movie_ratings)

            corr_df = pd.DataFrame(similar_movies, columns=['Correlation']).dropna()
            corr_df = corr_df.join(self.ratings['num of ratings'])

            # Filter based on min_ratings
            valid_corrs = corr_df[corr_df['num of ratings'] > self.min_ratings]

            for sim_movie, row in valid_corrs.iterrows():
                # Don't recommend movies the user has already rated
                if sim_movie not in user_ratings.index:
                    if sim_movie in recommendations:
                        recommendations[sim_movie] = max(recommendations[sim_movie], row['Correlation'])
                    else:
                        recommendations[sim_movie] = row['Correlation']

        # Sort by correlation and return top n
        top_recs = recommendations.sort_values(ascending=False).head(n)

        result = []
        for title, score in top_recs.items():
            result.append({
                'title': title,
                'score': float(score)
            })

        return result
