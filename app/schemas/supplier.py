import datetime

from pydantic import BaseModel

from app.schemas import ID_INT


class SupplierModel(BaseModel):
    name: str
    country: str
    address: str
    phone: str
    email: str


class SupplierFullModel(SupplierModel):
    id: ID_INT


class PatchSupplierModel(BaseModel):
    name: str | None = None
    country: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class DeleteSupplier(BaseModel):
    deleted_at: datetime.datetime
