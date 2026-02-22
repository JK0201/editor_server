from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services import download_documents, get_document, get_documents

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
)


# List documents
@router.get("")
async def get_documents_list(
    category_id: Annotated[int, Query()],
    session: AsyncSession = Depends(get_session),
    sort_by: Annotated[str, Query()] = "id",
    order: Annotated[str, Query()] = "asc",
    page: Annotated[int, Query()] = 1,
    size: Annotated[int, Query()] = 20,
    q: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
):
    return await get_documents(
        category_id,
        session,
        q,
        status,
        sort_by,
        order,
        page,
        size,
    )


# Get document by ID
@router.get("/{document_id}")
async def get_document_by_id(
    document_id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
):
    return await get_document(
        document_id,
        session,
    )


# Download single docx document by ID
@router.post("/download")
async def download_document_by_ids(
    document_ids: Annotated[list[int], Body()],
    session: AsyncSession = Depends(get_session),
):
    return await download_documents(document_ids, session)
