# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes
import uvicorn

# Importing config values for testing
from utils.config import MONGO_URI, REDIS_URL, OPENAI_API_KEY
print(f"Loaded MONGO_URI: {MONGO_URI}")
print(f"Loaded REDIS_URL: {REDIS_URL}")
print(f"Loaded OPENAI_API_KEY: {OPENAI_API_KEY}")

# Initialize FastAPI app
app = FastAPI()

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "✅ Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Run app directly (useful for local development)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
