import io
from datetime import datetime

from docx import Document as DocxDocument
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.script_line import ScriptLine
from app.models.speaker import Speaker


def format_docx(
    document: Document,
    speakers: dict,
    lines: list[ScriptLine],
) -> io.BytesIO:
    split_doc_title = document.title.split("_")
    recorded_date = split_doc_title[-2]
    recorded_time = split_doc_title[-1].split(".")[0]

    dt = datetime.strptime(f"{recorded_date}{recorded_time}", "%y%m%d%H%M%S")
    formatted_datetime = dt.strftime("%y.%m.%d - %H:%M:%S")

    doc = DocxDocument()
    doc.add_paragraph(formatted_datetime)
    doc.add_paragraph("")

    for line in lines:
        speaker_name = speakers.get(line.speaker_id, "Unknown")
        if line.start_time:
            text = f"{speaker_name} {line.start_time} {line.text}"
        else:
            text = f"{speaker_name}\t\t{line.text}"
        doc.add_paragraph(text)

    buffer = io.BytesIO()  # make empty buffer to save the document
    doc.save(buffer)  # save the document to the buffer
    buffer.seek(0)  # set the pointer to the beginning of the buffer
    return buffer


# TODO: has to be updated to single query with relationships later (next development + tuning phase)
async def make_docx(document_id: int, session: AsyncSession) -> tuple[str, io.BytesIO]:
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    speakers_result = await session.execute(
        select(Speaker).where(Speaker.document_id == document_id)
    )
    speakers = {s.id: s.name for s in speakers_result.scalars().all()}

    lines_result = await session.execute(
        select(ScriptLine)
        .where(ScriptLine.document_id == document_id)
        .order_by(ScriptLine.order)
    )
    lines = lines_result.scalars().all()

    title = document.title.replace(".txt", "")
    buffer = format_docx(document, speakers, lines)
    return title, buffer
