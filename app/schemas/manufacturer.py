import datetime

from pydantic import BaseModel

from app.schemas import ID_INT


class ManufacturerModel(BaseModel):
    name: str
    country: str
    address: str
    phone: str
    email: str


class ManufacturerFullModel(ManufacturerModel):
    id: ID_INT


class PatchManufacturerModel(BaseModel):
    name: str | None = None
    country: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class DeleteManufacturer(BaseModel):
    deleted_at: datetime.datetime
