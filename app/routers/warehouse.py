from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends import get_db, get_current_username
from app.schemas.warehouse import WarehouseFullModel, WarehouseModel, PatchWarehouseModel, \
    WarehouseWithSerialNumberModel
from app.services.warehouse import WarehouseService

router = APIRouter(
    prefix="/v1/warehouse",
    tags=["warehouse"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[WarehouseWithSerialNumberModel])
async def get_warehouses_with_serial_numbers(
    _: Annotated[str, Depends(get_current_username)],
    search: str | None = Query("", max_length=100),
    need_id: Annotated[list[int], Query()] = None,
    db: AsyncSession = Depends(get_db),
):
    return await WarehouseService(db=db).get_warehouse_with_serial_numbers(
        search=search,
        need_id=need_id,
    )


@router.post("/upload_excel_file/", status_code=status.HTTP_201_CREATED)
async def warehouse_upload_file(
    _: Annotated[str, Depends(get_current_username)],
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await WarehouseService(db=db).parse_excel_file(file=file)
    return {"status": 'File upload'}


@router.get(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=WarehouseFullModel,
)
async def get_one_warehouse(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await WarehouseService(db=db).get_warehouse(item_id=item_id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WarehouseFullModel)
async def create_new_warehouse(
    _: Annotated[str, Depends(get_current_username)],
    request: WarehouseModel,
    db: AsyncSession = Depends(get_db),
):
    return await WarehouseService(db=db).create_warehouse(request=request)


@router.patch(
    "/{item_id}/",
    status_code=status.HTTP_200_OK,
    response_model=WarehouseFullModel,
)
async def patch_warehouse(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    request: PatchWarehouseModel,
    db: AsyncSession = Depends(get_db),
):
    return await WarehouseService(db=db).update_warehouse(
        item_id=item_id,
        request=request,
    )


@router.delete("/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_warehouse(
    _: Annotated[str, Depends(get_current_username)],
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    await WarehouseService(db=db).delete_warehouse(item_id=item_id)
