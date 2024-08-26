from sqlalchemy import select, and_
from sqlalchemy.orm import contains_eager

from app.databases.dao.base_dao import BaseDAO
from app.models import Warehouse, SerialNumber


class WarehouseDAO(BaseDAO):
    model = Warehouse

    async def get_warehouse_by_name_and_article_with_serial_number(
            self,
            names: list[str] | None = None,
            articles: list[str] | None = None
    ):
        query = (
            select(self.model)
            .join(self.model.serial_numbers)
            .options(contains_eager(self.model.serial_numbers))
            .where(
                and_(
                    self.model.name.in_(names),
                    self.model.article.in_(articles)
                )
            )
            .where(self.model.deleted_at.is_(None))
        )
        q = await self.session.execute(query)
        results = q.scalars().unique().all()
        return results

    async def get_warehouse_by_name_with_serial_number_to_stock(
            self,
            names: list[str],
    ):
        query = (
            select(self.model)
            .join(self.model.serial_numbers)
            .options(contains_eager(self.model.serial_numbers))
            .where(self.model.name.in_(names))
            .where(self.model.deleted_at.is_(None))
            .where(SerialNumber.deleted_at.is_(None))
        )
        q = await self.session.execute(query)
        results = q.scalars().unique().all()
        return results
