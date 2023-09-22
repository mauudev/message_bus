from src.apps.users.domain import User
from src.logger import logger
from uuid import uuid4

class UsersRepository:
    """
    A dummy repository for user records
    """

    def add(self, user: User):
        logger.info(f"Adding a new user: {user}")
        user.id = str(uuid4())
        return user

    def update(self, user_id: int, user: User):
        logger.info(f"Updating user: {user} with id: {user_id}")

    def delete(self, user_id: int):
        logger.info(f"Deleting user with id: {user_id}")
