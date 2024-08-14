from abc import ABC
from typing import (
    Any,
    Iterable,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
)

from pydantic import BaseModel
from sqlalchemy import (
    delete,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import func

from app.databases.connect import Base

Model = TypeVar("Model", bound="Base")
BM = TypeVar("BM", bound=BaseModel)


class BaseDAO(ABC):
    model: Type[Base] = Base
    TKwargs = Optional[Any]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trans = self.session.begin()

    async def __aenter__(self):
        await self.trans.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.trans.__aexit__(exc_type, exc_val, exc_tb)
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def get_list(self, **kwargs: TKwargs) -> list[Model] | Any:
        query = self._construct_query(select(self.model), **kwargs)
        q = await self.session.execute(query)
        results = q.scalars().all()
        return results

    async def get_selected_list(
        self,
        select_: Iterable,
        **kwargs: TKwargs,
    ) -> list[Model] | Any:
        query = self._construct_query(select(*select_), **kwargs)
        q = await self.session.execute(query)
        results = q.scalars().all()
        return results

    async def get_one(self, **kwargs: TKwargs) -> Model | None:
        query = self._construct_query(select(self.model), **kwargs)
        q = await self.session.execute(query)
        return q.scalar_one_or_none()

    async def get_item_by_id(self, item_id: int, **kwargs: TKwargs) -> Optional[Model]:
        query = self._construct_query(select(self.model), **kwargs)
        try:
            q = await self.session.execute(query.where(self.model.id == item_id))
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        else:
            item: Optional[Model] = q.scalar_one_or_none()
        return item

    async def delete_item(self, item_id: int) -> bool:
        item = await self.get_item_by_id(item_id)
        if not item:
            return False
        try:
            await self.session.execute(
                delete(self.model).where(self.model.id == item_id),
            )
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return True

    async def delete_bulk(self, item_ids: list[int]) -> bool:
        items: list = await self.get_list(where=[self.model.id.in_(item_ids)])
        if not items:
            return False
        try:
            await self.session.execute(
                delete(self.model).where(self.model.id.in_(item_ids)),
            )
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return True

    async def create_item(
        self,
        item: BM,
        **kwargs: TKwargs,
    ) -> Optional[Model]:
        try:
            q = await self.session.execute(
                insert(self.model).values(**item.model_dump()).returning(self.model.id),
            )
            item_id = q.scalar_one()
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return await self.get_item_by_id(item_id, **kwargs)

    async def update_item(
        self,
        item_id: int,
        item: BM | dict[str, Any],
        exclude_none: bool = True,
        *,
        mode: Literal["json", "python"] = "python",
        **kwargs: TKwargs,
    ) -> Optional[Model]:
        if isinstance(item, BaseModel):
            item: dict[str, Any] = item.model_dump(exclude_none=exclude_none, mode=mode)
        try:
            await self.session.execute(
                update(self.model).where(self.model.id == item_id).values(**item),
            )
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return await self.get_item_by_id(item_id, **kwargs)

    async def _upd_sequence(self):
        query = await self.session.execute(select(func.max(self.model.id)))
        max_id_seq = query.scalar()
        if max_id_seq is None:
            max_id_seq = 1
            logger.warning(f"Can't to select {self.model.__tablename__} max id")
        query = text(
            f"select setval('{self.model.__tablename__}_id_seq', {max_id_seq})",
        )
        await self.session.execute(query)

    async def update_bulk(self, items: List[dict]) -> bool:
        try:
            await self.session.execute(update(self.model), items)
            await self.session.flush()
            return True
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise

    async def insert_bulk(self, items: List[dict]) -> bool:
        if not items:
            return False
        try:
            await self.session.execute(insert(self.model), items)
            await self.session.flush()
            return True
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise

    @staticmethod
    def _construct_query(
        query: Select,
        where: Optional[Iterable] = None,
        select_in_load: Optional[Iterable] = None,
        prepared_options: Optional[Iterable] = None,
        order_by: Optional[Iterable] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        group_by: Optional[Iterable] = None,
        join: Optional[Iterable] = None,
    ) -> Select:
        if where:
            query = query.where(*where)
        if select_in_load:
            for option in select_in_load:
                query = query.options(selectinload(option))
        if prepared_options:
            query = query.options(*prepared_options)
        if join:
            for model in join:
                query = query.join(model)
        if order_by:
            query = query.order_by(*order_by)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if group_by is not None:
            query = query.group_by(*group_by)

        return query
