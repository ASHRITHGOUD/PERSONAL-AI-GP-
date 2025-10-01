# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- FINAL CORRECTED IMPORTS ---
# Use relative imports: .routes.auth means look in the 'routes' folder for the 'auth.py' file.
from .routes.auth import router as auth_router
from .routes.chat_routes import router as chat_router

app = FastAPI()

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
# Include the router objects directly (router is the APIRouter instance from the files)
app.include_router(auth_router)
app.include_router(chat_router)