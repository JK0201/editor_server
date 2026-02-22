from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.utils.docx import make_merged_docx


async def get_categories(session: AsyncSession):
    result = await session.execute(select(Category))
    return result.scalars().all()


async def download_merged_documents(category_ids: list[int], session: AsyncSession):
    buffer = await make_merged_docx(category_ids, session)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx file type (HTTP protocol)
        headers={"Content-Disposition": "attachment; filename*=UTF-8''merged.docx"},
    )
