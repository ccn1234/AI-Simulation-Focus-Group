from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.simulation import router as simulation_router
from app.config import CORS_ORIGINS

app = FastAPI(title="AI Simulation Focus Group API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Simulation Focus Group API is running"}


app.include_router(simulation_router)
app.include_router(auth_router)
app.include_router(admin_router)
