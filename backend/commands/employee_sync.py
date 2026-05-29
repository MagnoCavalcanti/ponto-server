from backend.repositories import FuncionarioRepo
from backend.services import verificar_empresa
from .base import DesktopCommand, DesktopContext


class EmployeeSyncCommand(DesktopCommand):
    async def execute(self, payload: dict, context: DesktopContext) -> None:
        employees = payload["employees"]
        empresa_id = verificar_empresa(context.empresa, context.db)
        repo = FuncionarioRepo(dbsession=context.db)
        repo.bulk_insert_funcionario(employees, empresa_id)
