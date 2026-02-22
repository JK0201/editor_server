from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def get_categories(session: AsyncSession):
    result = await session.execute(select(Category))
    return {
        "status": status.HTTP_200_OK,
        "data": result.scalars().all(),
    }
