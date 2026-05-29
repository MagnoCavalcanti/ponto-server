from typing import Type

from .base import DesktopCommand
from .punch_record import PunchRecordCommand
from .employee_sync import EmployeeSyncCommand


COMMAND_REGISTRY: dict[str, Type[DesktopCommand]] = {
    "punch_record": PunchRecordCommand,
    "employee_sync": EmployeeSyncCommand,
}


def get_command(message_type: str) -> Type[DesktopCommand] | None:
    return COMMAND_REGISTRY.get(message_type)
