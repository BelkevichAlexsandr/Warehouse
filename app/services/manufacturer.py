import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.dao.manufacturer import ManufacturerDAO
from app.schemas.manufacturer import ManufacturerModel, PatchManufacturerModel


class ManufacturerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_manufacturers(
        self,
        search: str | None = None,
        need_id: list[int] | None = None,
    ):
        async with ManufacturerDAO(self.db) as dao:
            manufacturer_ids = []
            if need_id:
                manufacturer_ids = [dao.model.id.in_(need_id)]
            return await dao.get_list(
                where=[
                    dao.model.name.ilike(f"%{search}%"),
                    dao.model.deleted_at.is_(None),
                    *manufacturer_ids,
                ],
            )

    async def get_manufacturer(self, item_id: int):
        async with ManufacturerDAO(self.db) as dao:
            return await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            )

    async def create_manufacturer(self, request: ManufacturerModel):
        async with ManufacturerDAO(self.db) as dao:
            if await dao.get_one(
                where=[
                    dao.model.name == request.name,
                    dao.model.country == request.country,
                    dao.model.address == request.address,
                    dao.model.phone == request.phone,
                    dao.model.email == request.email,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Производитель с такими данными уже существует. Создание нового не возможно.",
                )
            return await dao.create_item(request)

    async def update_manufacturer(self, item_id: int, request: PatchManufacturerModel):
        async with ManufacturerDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Производитель с таким id {item_id} не существует. Обновление не возможно.",
                )
            return await dao.update_item(item_id=item_id, item=request)

    async def delete_manufacturer(self, item_id: int):
        async with ManufacturerDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Производитель с таким id {item_id} не существует. Удаление не возможно.",
                )
            await dao.update_item(
                item_id=item_id,
                item={"deleted_at": datetime.datetime.now()},
            )
