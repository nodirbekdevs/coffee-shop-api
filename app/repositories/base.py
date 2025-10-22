from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select, delete, desc, asc

from app.database import async_session_maker
from app.fields.common import ModelOrderByRule


class BaseRepository:
    model: DeclarativeBase

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    def _get_async_session(self) -> AsyncSession:
        if self.session:
            return self.session

        self.session = async_session_maker()
        return self.session

    @classmethod
    def get_model(cls):
        return cls.model

    async def add_one(self, data: dict, return_field: str = "id") -> int:
        model = self.get_model()
        async with self._get_async_session() as session:
            stmt = insert(model).values(**data).returning(getattr(model, return_field))
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def edit_one(self, pk: int, data: dict, return_field: str = "id") -> int:
        model = self.get_model()
        async with self._get_async_session() as session:
            stmt = (
                update(model)
                .where(model.id == pk)
                .values(**data)
                .returning(getattr(model, return_field))
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    @staticmethod
    def _generate_order_by(
        stmt, model: DeclarativeBase, orderings: list[ModelOrderByRule]
    ):
        ordering = []

        for rule in orderings:
            column = getattr(model, rule.field, None)
            if column:
                ordering.append(desc(column) if rule.desc else asc(column))

        if not ordering:
            return stmt

        return stmt.order_by(*ordering)

    async def find_all(
        self,
        fields: list[str] | tuple[str] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        orderings: list[ModelOrderByRule] | None = None,
        **filter_by,
    ):
        model = self.get_model()
        async with self._get_async_session() as session:
            if fields:
                columns = [getattr(model, field) for field in fields]
                stmt = select(*columns)
            else:
                stmt = select(model)

            stmt = stmt.filter_by(**{**filter_by, "is_active": True})

            if orderings:
                stmt = self._generate_order_by(
                    stmt=stmt, model=model, orderings=orderings
                )

            if skip:
                stmt = stmt.offset(skip)
            if limit:
                stmt = stmt.limit(limit)

            res = await session.execute(stmt)

            if not fields:
                return res.scalars().all()

            return res.mappings().all()

    async def find_one_or_none(
        self, fields: list[str] | tuple[str] | None = None, **filter_by
    ):
        model = self.get_model()
        async with self._get_async_session() as session:
            if fields:
                columns = [getattr(model, field) for field in fields]
                stmt = select(*columns)
            else:
                stmt = select(model)

            stmt = stmt.filter_by(**{**filter_by, "is_active": True})
            res = await session.execute(stmt)

            if not fields:
                return res.scalar_one_or_none()

            row = res.mappings().first()
            return row if row else None

    async def check_exist(self, **filter_by):
        model = self.get_model()
        async with self._get_async_session() as session:
            stmt = select(model.id).filter_by(**{**filter_by, "is_active": True})

            res = await session.execute(stmt)
            row = res.mappings().first()
            return row if row else None

    async def update_or_create(self, data: dict, **filter_by):
        exist = await self.find_one_or_none(fields=("id",), **filter_by)

        if exist:
            await self.update_if_exists(pk=exist['id'], data=data)
            return exist

        return await self.add_one(data=data, return_field="id")

    async def delete_one(self, **filter_by) -> bool | None:
        model = self.get_model()
        async with self._get_async_session() as session:
            async with session.begin():
                stmt = select(model).filter_by(**filter_by)
                result = await session.execute(stmt)
                instance = result.scalar_one_or_none()
                if not instance:
                    return None

                delete_stmt = delete(model).filter_by(**filter_by)
                await session.execute(delete_stmt)
                await session.commit()
                return True

    async def update_if_exists(
        self, pk: int, data: dict, return_field: str = "id"
    ) -> int | None:
        obj = await self.find_one_or_none(id=pk)

        if not obj:
            return None

        await self.edit_one(pk, data, return_field)
        return getattr(obj, return_field)

    async def bulk_update(
        self, data_list: list[dict], return_field: str = "id"
    ) -> list[int]:
        ids = []
        model = self.get_model()
        async with self._get_async_session() as session:
            for data in data_list:
                pk = data.pop("id")
                stmt = (
                    update(model)
                    .where(model.id == pk)
                    .values(**data)
                    .returning(getattr(model, return_field))
                )
                res = await session.execute(stmt)
                ids.append(res.scalar_one())
            await session.commit()
        return ids

    async def bulk_create(
        self, data_list: list[dict], return_field: str = "id"
    ) -> list[int]:
        model = self.get_model()
        async with self._get_async_session() as session:
            stmt = (
                insert(model).values(data_list).returning(getattr(model, return_field))
            )
            res = await session.execute(stmt)
            await session.commit()
        return [row[0] for row in res.fetchall()]

    async def delete_many(self, **filter_by) -> int:
        model = self.get_model()
        async with self._get_async_session() as session:
            count_stmt = select(model.id).filter_by(**{**filter_by, "is_active": True})
            count_result = await session.execute(count_stmt)
            records_to_delete = count_result.scalars().all()

            if not records_to_delete:
                return 0

            delete_stmt = delete(model).filter_by(**{**filter_by, "is_active": True})
            result = await session.execute(delete_stmt)
            await session.commit()

            return result.rowcount
