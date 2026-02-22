from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Speaker's ID for each document",
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documents.id"),
        comment="Document ID(FK)",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        default="New Speaker",
        comment="Speaker's Name",
    )
