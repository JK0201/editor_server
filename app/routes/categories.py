from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_session
from app.services import get_categories

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
