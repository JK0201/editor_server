from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services import get_document, get_documents

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
)


@router.get("")
async def list_documents(
    category_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await get_documents(
        category_id,
        session,
    )


@router.get("/{document_id}")
async def get_document_by_id(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await get_document(
        document_id,
        session,
    )
