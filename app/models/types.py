from enum import StrEnum


class SerialNumberStatusEnum(StrEnum):
    WAREHOUSE = "Склад"
    SUPPLIER = "Заказчик"
    SOLD = "Продано"
    EXECUTOR = "Исполнитель"
