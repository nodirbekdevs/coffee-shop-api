from datetime import timedelta

from sqlalchemy import select

from app.models.user import User
from app.utils.datetime import utc_now
from app.enums.user import UserStatusEnum
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def find_expired_unverified_users(self, expiry_days: int = 2):
        """Find unverified users older than specified days"""
        model = self.get_model()
        expiry_date = utc_now() - timedelta(days=expiry_days)

        async with self._get_async_session() as session:
            stmt = select(model).filter(
                model.status == UserStatusEnum.NOT_VERIFIED.value,
                model.created_at < expiry_date,
                model.is_active == True
            )
            result = await session.execute(stmt)
            return result.scalars().all()
