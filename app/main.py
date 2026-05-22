from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, analyse, translate

app = FastAPI(title="Bureaucracy Destroyer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analyse.router)
app.include_router(translate.router)

@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Bureaucracy Destroyer API",
        "version": "1.0.0"
    }