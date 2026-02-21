from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


async def get_documents(category_id: int, session: AsyncSession):
    result = await session.execute(
        select(Document).where(Document.category_id == category_id)
    )
    return result.scalars().all()
