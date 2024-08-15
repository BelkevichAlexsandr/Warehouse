from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import supplier, manufacturer

app = FastAPI(
    title="NameProject",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(supplier.router)
app.include_router(manufacturer.router)
