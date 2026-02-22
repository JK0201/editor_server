from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class ScriptLine(Base):
    __tablename__ = "script_lines"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Script line ID",
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documents.id"),
        comment="Document ID(FK)",
    )

    speaker_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("speakers.id"),
        comment="Speaker ID(FK)",
    )

    text: Mapped[str] = mapped_column(
        Text,
        comment="Script line text",
    )

    start_time: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Start time (MM:SS)",
    )

    order: Mapped[int] = mapped_column(
        default=0,
        comment="Line order",
    )
