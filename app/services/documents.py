from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.script_line import ScriptLine
from app.models.speaker import Speaker


async def get_documents(
    category_id: int,
    session: AsyncSession,
    q: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    size: int = 20,
):
    query = select(Document).where(Document.category_id == category_id)

    # User search query (title)
    if q:
        query = query.where(Document.title.ilike(f"%{q}%"))

    # filter by status
    if status:
        query = query.where(Document.status == status)

    # sort by
    sort_column = {
        "id": Document.id,
        "title": Document.title,
        "file_size": Document.file_size,
        "updated_at": Document.updated_at,
    }.get(sort_by, Document.id)

    # order by
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # offset and limit
    query = query.offset((page - 1) * size).limit(size)

    result = await session.execute(query)
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


# Download docx document by ID
