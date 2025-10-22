from sqlalchemy.orm import declared_attr

from app.database import Base
from app.models.abstract import (
    IdAbstractModel,
    IsActiveAbstractModel,
    CreatedAtAbstractModel,
    UpdatedAtAbstractModel,
)


class BaseModel(
    Base, IsActiveAbstractModel, CreatedAtAbstractModel, UpdatedAtAbstractModel
):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseModelWithId(BaseModel, IdAbstractModel):
    __abstract__ = True
