from pydantic import BaseModel

from app.schemas import ID_INT
from app.schemas.serial_number import SerialNumberFullModel


class WarehouseModel(BaseModel):
    manufacturer_id: ID_INT
    supplier_id: ID_INT
    article: str
    name: str
    warranty: int
    product_count_in_stock: int | None = None
    product_count_out: int | None = None
    position: str | None = None
    description: str | None = None


class WarehouseFullModel(WarehouseModel):
    id: ID_INT


class PatchWarehouseModel(BaseModel):
    manufacturer_id: ID_INT | None = None
    supplier_id: ID_INT | None = None
    article: str | None = None
    name: str | None = None
    warranty: int | None = None
    product_count_in_stock: int | None = None
    product_count_out: int | None = None
    position: str | None = None
    description: str | None = None


class WarehouseWithSerialNumberModel(WarehouseFullModel):
    serial_numbers: list[SerialNumberFullModel] | None = None
