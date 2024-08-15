import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.dao.supplier import SupplierDAO
from app.schemas.supplier import SupplierModel, PatchSupplierModel


class SupplierService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_suppliers(
        self,
        search: str,
        need_id: list[int] | None = None,
    ):
        async with SupplierDAO(self.db) as dao:
            supplier_ids = []
            if need_id:
                supplier_ids = [dao.model.id.in_(need_id)]
            return await dao.get_list(
                    where=[
                        dao.model.name.ilike(f"%{search}%"),
                        dao.model.deleted_at.is_(None),
                        *supplier_ids,
                    ],
                )

    async def get_supplier(self, item_id: int):
        async with SupplierDAO(self.db) as dao:
            return await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ]
            )

    async def create_supplier(self, request: SupplierModel):
        async with SupplierDAO(self.db) as dao:
            if await dao.get_one(
                where=[
                    dao.model.name == request.name,
                    dao.model.country == request.country,
                    dao.model.address == request.address,
                    dao.model.phone == request.phone,
                    dao.model.email == request.email,
                    dao.model.deleted_at.is_(None),
                ]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Поставщик с такими параметрами уже существует. Создание нового не возможно.',
                )
            return await dao.create_item(request)

    async def update_supplier(self, item_id: int, request: PatchSupplierModel):
        async with SupplierDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Поставщик с таким id {item_id} не существует. Обновление не возможно.',
                )
            return await dao.update_item(item_id=item_id, item=request)

    async def delete_supplier(self, item_id: int):
        async with SupplierDAO(self.db) as dao:
            if not await dao.get_one(
                where=[
                    dao.model.id == item_id,
                    dao.model.deleted_at.is_(None),
                ]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Поставщик с таким id {item_id} не существует. Удаление не возможно.',
                )
            await dao.update_item(item_id=item_id, item={'deleted_at': datetime.datetime.now()})
