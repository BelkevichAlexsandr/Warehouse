from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends import get_db
from app.schemas.manufacturer import (
    ManufacturerFullModel, ManufacturerModel,
    PatchManufacturerModel,
)
from app.services.manufacturer import ManufacturerService

router = APIRouter(
    prefix="/v1/manufacturer",
    tags=["manufacturer"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[ManufacturerFullModel],
)
async def get_manufacturers(
    search: str | None = Query("", max_length=100),
    need_id: Annotated[list[int], Query()] = None,
    db: AsyncSession = Depends(get_db),
):
    return await ManufacturerService(db=db).get_all_manufacturers(
        search=search,
        need_id=need_id,
    )


@router.get(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ManufacturerFullModel,
)
async def get_one_manufacturer(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await ManufacturerService(db=db).get_manufacturer(item_id=item_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ManufacturerFullModel,
)
async def create_new_manufacturer(
    request: ManufacturerModel,
    db: AsyncSession = Depends(get_db),
):
    return await ManufacturerService(db=db).create_manufacturer(request=request)


@router.patch(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ManufacturerFullModel,
)
async def patch_manufacturer(
    item_id: int,
    request: PatchManufacturerModel,
    db: AsyncSession = Depends(get_db),
):
    return await ManufacturerService(db=db).update_manufacturer(
        item_id=item_id,
        request=request,
    )


@router.delete("/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_manufacturer(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    await ManufacturerService(db=db).delete_manufacturer(item_id=item_id)
