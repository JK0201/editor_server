from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.script_line import ScriptLine
from app.models.speaker import Speaker


async def get_documents(category_id: int, session: AsyncSession):
    result = await session.execute(
        select(Document)
        .where(Document.category_id == category_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


#  TODO: has to be updated to single query with relationships later (next development + tuning phase)
async def get_document(document_id: int, session: AsyncSession):
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    speakers = await session.execute(
        select(Speaker).where(Speaker.document_id == document_id)
    )

    script_lines = await session.execute(
        select(ScriptLine)
        .where(ScriptLine.document_id == document_id)
        .order_by(ScriptLine.order)
    )

    return {
        "document": document,
        "speakers": speakers.scalars().all(),
        "script_lines": script_lines.scalars().all(),
    }
