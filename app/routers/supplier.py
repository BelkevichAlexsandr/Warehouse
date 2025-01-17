from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends import get_db, get_current_username
from app.schemas.supplier import (
    PatchSupplierModel, SupplierFullModel,
    SupplierModel,
)
from app.services.supplier import SupplierService

router = APIRouter(
    prefix="/v1/supplier",
    tags=["supplier"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[SupplierFullModel])
async def get_suppliers(
    _: Annotated[str, Depends(get_current_username)],
    search: str | None = Query("", max_length=100),
    need_id: Annotated[list[int], Query()] = None,
    db: AsyncSession = Depends(get_db),
):
    return await SupplierService(db=db).get_all_suppliers(
        search=search,
        need_id=need_id,
    )


@router.get(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SupplierFullModel,
)
async def get_one_supplier(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await SupplierService(db=db).get_supplier(item_id=item_id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SupplierFullModel)
async def create_new_supplier(
    _: Annotated[str, Depends(get_current_username)],
    request: SupplierModel,
    db: AsyncSession = Depends(get_db),
):
    return await SupplierService(db=db).create_supplier(request=request)


@router.patch(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SupplierFullModel,
)
async def patch_supplier(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    request: PatchSupplierModel,
    db: AsyncSession = Depends(get_db),
):
    return await SupplierService(db=db).update_supplier(
        item_id=item_id,
        request=request,
    )


@router.delete("/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_supplier(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    await SupplierService(db=db).delete_supplier(item_id=item_id)
