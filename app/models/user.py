from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.user import UserStatusEnum, UserRoleEnum

from app.models.base import Base, BaseModelWithId


class User(BaseModelWithId):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(300))
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    role: Mapped[UserRoleEnum] = mapped_column(
        SQLEnum(UserRoleEnum),
        default=UserRoleEnum.USER.value
    )
    status: Mapped[UserStatusEnum] = mapped_column(SQLEnum(UserStatusEnum))

    verifications: Mapped[list["Verification"]] = relationship(
        "Verification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self):
        return f"{self.id} - {self.email}"

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
