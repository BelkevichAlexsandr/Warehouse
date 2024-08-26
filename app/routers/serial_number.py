from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends import get_db, get_current_username
from app.schemas.serial_number import (
    PatchSerialNumberModel, SerialNumberFullModel,
    SerialNumberModel,
)
from app.services.serial_number import SerialNumberService

router = APIRouter(
    prefix="/v1/serial_number",
    tags=["serial_number"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[SerialNumberFullModel])
async def get_serial_numbers(
    _: Annotated[str, Depends(get_current_username)],
    search: str | None = Query("", max_length=100),
    need_id: Annotated[list[int], Query()] = None,
    db: AsyncSession = Depends(get_db),
):
    return await SerialNumberService(db=db).get_all_serial_numbers(
        search=search,
        need_id=need_id,
    )


@router.get(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SerialNumberFullModel,
)
async def get_one_serial_number(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await SerialNumberService(db=db).get_serial_number(item_id=item_id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SerialNumberFullModel)
async def create_new_serial_number(
    _: Annotated[str, Depends(get_current_username)],
    request: SerialNumberModel,
    db: AsyncSession = Depends(get_db),
):
    return await SerialNumberService(db=db).create_serial_number(request=request)


@router.patch(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SerialNumberFullModel,
)
async def patch_serial_number(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    request: PatchSerialNumberModel,
    db: AsyncSession = Depends(get_db),
):
    return await SerialNumberService(db=db).update_serial_number(
        item_id=item_id,
        request=request,
    )


@router.delete("/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_serial_number(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    await SerialNumberService(db=db).delete_serial_number(item_id=item_id)
