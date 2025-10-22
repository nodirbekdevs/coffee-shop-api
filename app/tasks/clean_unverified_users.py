import asyncio

from app.celery import celery
from app.repositories import UserRepository, VerificationRepository



async def cleanup_unverified_users():
    """Delete users who haven't verified within 2 days"""
    user_repository = UserRepository()
    verification_repository = VerificationRepository()

    unverified_users = await user_repository.find_expired_unverified_users(expiry_days=2)

    deleted_count = 0
    for user in unverified_users:
        await verification_repository.delete_many(user_id=user.id)
        await user_repository.delete_one(pk=user.id)
        deleted_count += 1

    return f"Deleted {deleted_count} unverified users"


@celery.task
def task_cleanup_unverified_users():
    asyncio.run(cleanup_unverified_users())