import csv
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import Noul, TypeSafeClient

def load_movies(filepath: str) -> list[str]:
    movies = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                movies.append(row[1])
    return movies

def mock_fast_search(query: str, movies: list[str], top_k: int = 10) -> list[str]:
    """
    Mock fast search (e.g. BM25 replacement).
    Since we only have titles, we will just do a simple keyword match or return random candidates.
    In a real scenario, this would use embeddings or BM25 over plot descriptions.
    """
    query_words = set(query.lower().split())

    def score(title):
        title_words = set(title.lower().split())
        return len(query_words.intersection(title_words))

    scored_movies = [(title, score(title)) for title in movies]
    scored_movies.sort(key=lambda x: x[1], reverse=True)

    # If no keywords matched, just pick random movies
    if scored_movies[0][1] == 0:
        candidates = random.sample(movies, top_k)
    else:
        candidates = [m[0] for m in scored_movies[:top_k]]

    return candidates

def recommend_movie(query: str, movies: list[str]) -> list[tuple[str, float]]:
    candidates = mock_fast_search(query, movies, top_k=10)

    api_key = os.environ.get("TYPESAFE_API_KEY", "placeholder_api_key")
    client = TypeSafeClient(api_key=api_key)

    is_good_recommendation = Noul(
        instructions=(
            f"The user is looking for a movie recommendation based on this query: '{query}'. "
            "Could this candidate movie be a good recommendation for the user? "
            "It must fit the genre, theme, or entities mentioned in the user's query, "
            "and not be unrelated."
        ),
    )

    def score_candidate(candidate: str) -> tuple[str, float]:
        try:
            response = client.system_one(
                state={"user_query": query, "candidate_movie": candidate},
                questions={"is_match": is_good_recommendation},
            )
            return candidate, response.nouls["is_match"].noul
        except Exception as e:
            # Catch exceptions like authorization errors (since we use a placeholder key)
            print(f"Error calling TypeSafe API for '{candidate}': {e}")
            return candidate, 0.0

    scored_candidates = []
    # Limit max_workers to avoid hitting rate limits too hard if using a real key
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = pool.map(score_candidate, candidates)
        for result in results:
            scored_candidates.append(result)

    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    return scored_candidates

if __name__ == "__main__":
    movies = load_movies("datasets/Movie_Id_Titles.txt")
    query = "A funny comedy with Jim Carrey"

    print(f"User Query: {query}")
    print("Fetching candidates and re-ranking using TypeSafe AI...")

    recommendations = recommend_movie(query, movies)

    print("\nRecommendations:")
    for title, score in recommendations:
        print(f"[{score:.2f}] {title}")
