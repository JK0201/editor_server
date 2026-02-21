from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Category ID",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        default="New Category",
        comment="Category Name",
    )
