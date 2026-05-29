from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import WebSocket
from sqlalchemy.orm import Session

from backend.services import ConnectionManager


@dataclass
class DesktopContext:
    empresa: str
    websocket: WebSocket
    manager: ConnectionManager
    db: Session


class DesktopCommand(ABC):
    @abstractmethod
    async def execute(self, payload: dict, context: DesktopContext) -> None:
        pass
