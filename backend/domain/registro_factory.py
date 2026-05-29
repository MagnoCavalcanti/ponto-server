"""Factory Method: criação de RegistroPonto conforme a origem dos dados."""

from abc import ABC, abstractmethod

from backend.schemas import RegistroPonto
from backend.models import RegistroPonto as RegistroModel
from backend.adapters import RepRegistroAdapter


class RegistroFactory(ABC):
    @abstractmethod
    def create(self) -> RegistroModel:
        pass


class RegistroFromSchemaFactory(RegistroFactory):
    """Factory para registros vindos da API (schema Pydantic)."""

    def __init__(self, ponto: RegistroPonto):
        self._ponto = ponto

    def create(self) -> RegistroModel:
        return RegistroModel(**self._ponto.model_dump(exclude_unset=True))


class RegistroFromRepFactory(RegistroFactory):
    """Factory para registros vindos da sincronização com o REP."""

    def __init__(
        self,
        adapter: RepRegistroAdapter,
        empresa_id: int,
        relogio_id: int,
        tipo: str,
    ):
        self._adapter = adapter
        self._empresa_id = empresa_id
        self._relogio_id = relogio_id
        self._tipo = tipo

    def create(self) -> RegistroModel:
        return RegistroModel(
            nsr=self._adapter.nsr,
            cpf_funcionario=self._adapter.cpf,
            empresa_id=self._empresa_id,
            relogio_id=self._relogio_id,
            data=self._adapter.data,
            hora=self._adapter.hora,
            tipo=self._tipo,
        )
