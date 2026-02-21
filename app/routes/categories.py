from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services import get_categories

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["categories"],
)


@router.get("")
async def list_categories(session: AsyncSession = Depends(get_session)):
    return await get_categories(session)
