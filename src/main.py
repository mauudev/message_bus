from src.apps.users.usecases import *
from src.bus_framework import bus_framework
from src.logger import logger

logger.info(
    f"HANDLERS: {bus_framework.bus.command_handlers_reg} -> {bus_framework.bus.event_handlers_reg}"
)

new_user_cmd = CreateNewUserCommand(name="John Doe", email="johndoe@me.com")
response = bus_framework(new_user_cmd)
logger.info(f"RESPONSE: {response}")
