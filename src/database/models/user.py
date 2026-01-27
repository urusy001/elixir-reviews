from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    accepted_terms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    drafts: Mapped[list["SharedResultDraft"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
