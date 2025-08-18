from fastapi import FastAPI
from routes import chat_routes

app = FastAPI(title="Personal AI Backend")

# include chat routes
app.include_router(chat_routes.router)

@app.get("/")
def root():
    return {"message": "Personal AI Backend is running 🚀"}
