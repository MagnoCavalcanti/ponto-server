from backend.repositories import PontoRepo
from .base import DesktopCommand, DesktopContext


class PunchRecordCommand(DesktopCommand):
    async def execute(self, payload: dict, context: DesktopContext) -> None:
        registers = payload["registers"]
        empresa_id = payload.get("empresa_id", 1)
        relogio_id = payload.get("relogio_id", 1)

        repo = PontoRepo(dbsession=context.db)
        repo.sync_registers(
            registers,
            empresa_id=empresa_id,
            relogio_id=relogio_id,
        )
        await context.manager.send_personal_message(
            "created", context.empresa, context.websocket
        )
