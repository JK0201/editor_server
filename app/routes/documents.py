from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_session
from app.schemas import ScriptLineDiff
from app.services import (
    download_documents,
    get_document,
    get_documents,
    sync_script_lines,
)

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
    progress: Annotated[str | None, Query()] = None,
):
    result = await get_documents(
        category_id,
        session,
        q,
        progress,
        sort_by,
        order,
        page,
        size,
    )
    return {
        "status": status.HTTP_200_OK,
        "data": result,
    }


# Get document by ID
@router.get("/{document_id}")
async def get_document_by_id(
    document_id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
):
    result = await get_document(document_id, session)
    return {
        "status": status.HTTP_200_OK,
        "data": result,
    }


# Download single docx document by ID
@router.post("/download")
async def download_document_by_ids(
    document_ids: Annotated[list[int], Body()],
    session: AsyncSession = Depends(get_session),
):
    return await download_documents(document_ids, session)


@router.patch("/{document_id}/script_lines")
async def patch_script_lines(
    document_id: Annotated[int, Path()],
    data: ScriptLineDiff,
    session: AsyncSession = Depends(get_session),
):
    result = await sync_script_lines(document_id, data, session)
    return {
        "status": status.HTTP_200_OK,
        "data": result,
    }
