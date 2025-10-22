from datetime import datetime

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.datetime import utc_now


class IdAbstractModel:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class IsActiveAbstractModel:
    is_active: Mapped[bool] = mapped_column(default=True)


class CreatedAtAbstractModel:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class UpdatedAtAbstractModel:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
