import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class DocumentStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Document ID",
    )

    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categories.id"),
        comment="Category ID(FK)",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        default="New Document",
        comment="Document Title",
    )

    audio_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Audio URL from bucket storage",
    )

    file_size: Mapped[int] = mapped_column(
        default=0,
        comment="File size in bytes",
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.PENDING,
        comment="Document processing status",
    )
