import asyncio

from app.celery import celery
from app.repositories import UserRepository, VerificationRepository


@celery.task
def task_cleanup_unverified_users():
    async def async_cleanup():
        user_repository = UserRepository()
        verification_repository = VerificationRepository()

        unverified_users = await user_repository.find_expired_unverified_users(expiry_days=2)

        deleted_count = 0
        for user in unverified_users:
            await verification_repository.delete_many(user_id=user.id)
            await user_repository.delete_one(id=user.id)
            deleted_count += 1

        return f"Deleted {deleted_count} unverified users"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(async_cleanup())
        return result
    finally:
        loop.close()