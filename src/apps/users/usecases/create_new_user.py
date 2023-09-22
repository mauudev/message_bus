from dataclasses import dataclass

from src.apps.users.domain import User
from src.apps.users.domain.repositories.users_repository import UsersRepository
from src.core.base_abstractions import Command, CommandResponse, Event, Handler


@dataclass(kw_only=True)
class CreateNewUserCommand(Command):
    name: str
    email: str


@dataclass(kw_only=True)
class CreateNewUserResponse(CommandResponse):
    id: str
    name: str
    email: str


class CreateNewUser(Handler):
    def handle(self, command: CreateNewUserCommand) -> CreateNewUserResponse:
        user = User(name=command.name, email=command.email)
        repository = UsersRepository()
        repository.add(user)
        return CreateNewUserResponse(id=user.id, name=user.name, email=user.email)
