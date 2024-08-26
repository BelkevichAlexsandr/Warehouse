from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic

from app.routers import manufacturer, supplier, warehouse, serial_number

app = FastAPI(
    title="Warehouse",
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
app.include_router(warehouse.router)
app.include_router(serial_number.router)
