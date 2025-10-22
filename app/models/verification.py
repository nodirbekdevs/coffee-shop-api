from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey

from app.enums.auth import (
    ContactTypeEnum,
    VerificationMethodEnum,
)
from app.models.base import Base, BaseModelWithId


class Verification(BaseModelWithId):
    contact: Mapped[str] = mapped_column(String(255), index=True)
    contact_type: Mapped[ContactTypeEnum] = mapped_column(SQLEnum(ContactTypeEnum))

    security_code: Mapped[str] = mapped_column(String(255))
    operator: Mapped[str] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(50), nullable=True)

    method: Mapped[VerificationMethodEnum] = mapped_column(SQLEnum(VerificationMethodEnum))
    is_verified: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="verifications",
    )