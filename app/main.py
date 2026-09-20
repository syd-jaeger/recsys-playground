from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.data.loader import MovieLensLoader
from src.models.collaborative import ItemBasedCFRecommender
from src.models.llm_stub import LLMRecommender

app = FastAPI(title="AI Recommendation System API")

# Setup CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold data and models
loader = None
models = {}

@app.on_event("startup")
def load_resources():
    global loader, models
    # Initialize and load dataset
    loader = MovieLensLoader()
    data = loader.load_data()

    # Initialize and fit models
    cf_model = ItemBasedCFRecommender(min_ratings=100)
    cf_model.fit(data)

    llm_model = LLMRecommender()
    llm_model.fit(data)

    models = {
        "collaborative": cf_model,
        "llm_stub": llm_model
    }

@app.get("/api/models")
def get_models():
    return {"models": list(models.keys())}

@app.get("/api/users")
def get_users():
    if not loader:
        raise HTTPException(status_code=500, detail="Data not loaded")
    users = loader.get_users()
    # Return first 50 users for demonstration to avoid overloading frontend
    return {"users": users[:50]}

@app.get("/api/user/{user_id}/history")
def get_user_history(user_id: int):
    if not loader:
        raise HTTPException(status_code=500, detail="Data not loaded")
    history = loader.get_user_history(user_id)
    return {"history": history}

@app.get("/api/recommend/{user_id}")
def get_recommendations(user_id: int, model: str = "collaborative", n: int = 5):
    if model not in models:
        raise HTTPException(status_code=400, detail=f"Model {model} not found.")

    try:
        recs = models[model].recommend(user_id, n=n)
        return {"recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files to serve the frontend
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
