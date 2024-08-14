import datetime

from sqlalchemy import (
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.databases.connect import Base
from app.models.types import SerialNumberStatusEnum


class BaseClass:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    deleted_at: Mapped[datetime.datetime | None]
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        default=func.now(),
        onupdate=func.current_timestamp(),
    )


class WarehouseSerialNumber(BaseClass, Base):
    __tablename__ = "warehouse_serial_number"

    serial_number_id: Mapped[int] = mapped_column(ForeignKey("serial_number.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.id"))


class SerialNumber(BaseClass, Base):
    __tablename__ = "serial_number"

    name: Mapped[str]
    status: Mapped[SerialNumberStatusEnum] = mapped_column(default=SerialNumberStatusEnum.WAREHOUSE)
    data_input: Mapped[datetime.date] = mapped_column(default=func.now())
    data_output: Mapped[datetime.date | None]
    employee_id: Mapped[int | None]

    warehouses: Mapped[list["Warehouse"]] = relationship(
        secondary=WarehouseSerialNumber.__tablename__,
        back_populates="serial_numbers",
    )


class Warehouse(BaseClass, Base):
    __tablename__ = "warehouse"

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"))

    article: Mapped[str]
    name: Mapped[str]
    price_enter: Mapped[int]
    warranty: Mapped[int]
    product_count_in_stock: Mapped[int]
    product_count_out: Mapped[int | None]

    manufacturer: Mapped["Manufacturer"] = relationship(back_populates='warehouses')
    serial_numbers: Mapped[list["SerialNumber"]] = relationship(
        secondary=WarehouseSerialNumber.__tablename__,
        back_populates="warehouses",
    )
    supplier: Mapped["Supplier"] = relationship(back_populates='warehouses')


class Supplier(BaseClass, Base):
    __tablename__ = "supplier"

    name: Mapped[str]
    country: Mapped[str]
    address: Mapped[str]
    phone: Mapped[str]
    email: Mapped[str]

    warehouses: Mapped[list["Warehouse"]] = relationship(back_populates="supplier")


class Manufacturer(BaseClass, Base):
    __tablename__ = "manufacturer"

    name: Mapped[str]
    country: Mapped[str]
    address: Mapped[str]
    phone: Mapped[str]
    email: Mapped[str]

    warehouses: Mapped[list["Warehouse"]] = relationship(back_populates="manufacturer")

