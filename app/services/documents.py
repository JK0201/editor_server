import asyncio
from urllib.parse import quote

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.script_line import ScriptLine
from app.models.speaker import Speaker
from app.schemas import ScriptLineDiff
from app.utils import generate_presigned_url, make_docx, make_zip


async def get_documents(
    category_id: int,
    session: AsyncSession,
    q: str | None = None,
    progress: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    size: int = 20,
):
    query = select(Document).where(Document.category_id == category_id)

    # User search query (title)
    if q:
        query = query.where(Document.title.ilike(f"%{q}%"))

    # filter by progress
    if progress:
        query = query.where(Document.status == progress)

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
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
        "audio_presigned_url": generate_presigned_url(document.audio_url),
        "speakers": speakers.scalars().all(),
        "script_lines": script_lines.scalars().all(),
    }


# Download docx document by ID
async def download_documents(document_ids: list[int], session: AsyncSession):
    if len(document_ids) == 1:
        title, buffer = await make_docx(document_ids[0], session)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx file type (HTTP protocol)
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(title)}.docx"  # download immidiately without opening in browser
            },
        )

    results = await asyncio.gather(
        *[make_docx(doc_id, session) for doc_id in document_ids]
    )
    zip_buffer = make_zip([f"{title}.docx", buffer] for title, buffer in results)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''documents.zip"},
    )


async def sync_script_lines(
    document_id: int,
    diff: ScriptLineDiff,
    session: AsyncSession,
):
    # 1. Check if document exists + create temp values for speakers and lines
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    speaker_temp_map: dict[str, int] = {}
    line_temp_map: dict[str, int] = {}

    # 2. delete speakers first, if diff.speakers.deleted != []
    if diff.speakers.deleted:
        await session.execute(
            delete(Speaker).where(Speaker.id.in_(diff.speakers.deleted))  # bulk delete
        )

    # 3. create speakers, if diff.speakers.created != [] by loop
    # 해당 Speaker 객체를 트랜젝션 메니저에 올린 후 -> flush() -> 반환 받은 id를 temp에 저장 (커밋은 안함)
    for spk in diff.speakers.created:
        new_speaker = Speaker(document_id=document_id, name=spk.name)
        session.add(new_speaker)  # add to transaction
        await session.flush()  # flush to get the new speaker id
        speaker_temp_map[spk.temp_id] = new_speaker.id

    # 4. update speaker's name, if diff.speakers.updated != [] by loop
    for spk in diff.speakers.updated:
        await session.execute(
            update(Speaker).where(Speaker.id == spk.id).values(name=spk.name)
        )

    # 5. delete script lines first, if diff.deleted != []
    if diff.deleted:
        await session.execute(
            delete(ScriptLine).where(ScriptLine.id.in_(diff.deleted))  # bulk delete
        )

    # 6. create script lines, if diff.created != [] by loop
    for line in diff.created:
        # temp_id (새로 추가된 화자의 id)면, speaker_temp_map에서 flush후 받은 실제 id 사용
        # 기존 화자 id면, 그대로 사용
        real_speaker_id = speaker_temp_map.get(line.speaker_id) or int(line.speaker_id)
        new_line = ScriptLine(
            document_id=document_id,
            speaker_id=real_speaker_id,
            text=line.text,
            start_time=line.start_time,
            order=line.order,
        )
        session.add(new_line)
        await session.flush()
        line_temp_map[line.temp_id] = new_line.id

    # 7. update script lines, if diff.updated != [] by loop
    for line in diff.updated:
        values = line.model_dump(exclude_unset=True)  # 요청으로 들어온 필드값만 추출
        values.pop("id")  # exclude id from values (id is primary key)
        if values:
            await session.execute(
                update(ScriptLine)
                .where(ScriptLine.id == line.id)
                .values(**values)  # **unpaking
            )

    # 8. re-order script lines, if diff.orders != [] by loop
    for item in diff.orders:
        await session.execute(
            update(ScriptLine).where(ScriptLine.id == item.id).values(order=item.order)
        )

    # 9. status update, if diff.status is not None
    if diff.status:
        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=diff.status)
        )

    # 10. commit all changes
    await session.commit()

    return {
        "speakers": list(speaker_temp_map.items()),
        "lines": list(line_temp_map.items()),
    }
