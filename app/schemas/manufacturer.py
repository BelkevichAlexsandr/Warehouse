import datetime

from pydantic import BaseModel

from app.schemas import ID_INT


class ManufacturerModel(BaseModel):
    name: str
    country: str


class ManufacturerFullModel(ManufacturerModel):
    id: ID_INT


class PatchManufacturerModel(BaseModel):
    name: str | None = None
    country: str | None = None


class DeleteManufacturer(BaseModel):
    deleted_at: datetime.datetime
