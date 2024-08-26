import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.dao.serial_number import SerialNumberDAO
from app.schemas.serial_number import PatchSerialNumberModel, SerialNumberModel


class SerialNumberService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_serial_numbers(
        self,
        search: str | None = None,
        need_id: list[int] | None = None,
    ):
        async with SerialNumberDAO(self.db) as dao:
            serial_numbers_ids = []
            if need_id:
                serial_numbers_ids = [dao.model.id.in_(need_id)]
            return await dao.get_list(
                where=[
                    dao.model.name.ilike(f"%{search}%"),
                    dao.model.deleted_at.is_(None),
                    *serial_numbers_ids,
                ],
            )

    async def get_serial_number(self, item_id: int):
        async with SerialNumberDAO(self.db) as dao:
            return await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            )

    async def create_serial_number(self, request: SerialNumberModel):
        async with SerialNumberDAO(self.db) as dao:
            if await dao.get_one(
                where=[
                    dao.model.name == request.name,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Серийный номер с такими параметрами уже существует. Создание нового не возможно.",
                )
            return await dao.create_item(request)

    async def update_serial_number(self, item_id: int, request: PatchSerialNumberModel):
        async with SerialNumberDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Серийный номер с таким id {item_id} не существует. Обновление не возможно.",
                )
            return await dao.update_item(item_id=item_id, item=request)

    async def delete_serial_number(self, item_id: int):
        async with SerialNumberDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Серийный номер с таким id {item_id} не существует. Удаление не возможно.",
                )
            await dao.update_item(
                item_id=item_id,
                item={"deleted_at": datetime.datetime.now()},
            )