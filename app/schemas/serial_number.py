import datetime

from pydantic import BaseModel

from app.models import SerialNumberStatusEnum
from app.schemas import ID_INT


class SerialNumberModel(BaseModel):
    warehouse_id: ID_INT
    name: str
    status: SerialNumberStatusEnum
    price_input: int
    price_output: int | None
    data_input: datetime.date
    data_output: datetime.date | None
    employee_id: int | None
    buyer_id: int | None
    order_id: int | None


class SerialNumberFullModel(SerialNumberModel):
    id: ID_INT


class PatchSerialNumberModel(BaseModel):
    warehouse_id: ID_INT | None = None
    name: str | None = None
    status: SerialNumberStatusEnum | None = None
    price_input: int | None = None
    price_output: int | None = None
    data_input: datetime.date | None = None
    data_output: datetime.date | None = None
    employee_id: int | None = None
    buyer_id: int | None = None
    order_id: int | None = None
