from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_session
from app.services import download_merged_documents, get_categories

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["categories"],
)


# List categories
@router.get("")
async def get_categories_list(session: AsyncSession = Depends(get_session)):
    result = await get_categories(session)
    return {
        "status": status.HTTP_200_OK,
        "data": result,
    }


@router.post("/download")
async def download_merged_by_category(
    category_ids: Annotated[list[int], Body()],
    session: AsyncSession = Depends(get_session),
):
    return await download_merged_documents(category_ids, session)
