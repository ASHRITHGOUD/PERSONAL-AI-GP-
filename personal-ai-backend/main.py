from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes

app = FastAPI(title="Personal AI Backend")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "✅ Backend is running"}
