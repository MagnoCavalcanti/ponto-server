from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import status, HTTPException
from pydantic import ValidationError
from typing import List

from backend.schemas import RegistroPonto
from backend.models import RegistroPonto as Registro_models
from backend.adapters import RepRegistroAdapter
from backend.domain import RegistroFromSchemaFactory, RegistroFromRepFactory
from .funcionario_repo import FuncionarioRepo


class PontoRepo:

    def __init__(self, dbsession: Session):
        self.db = dbsession

    def Bater_Ponto(self, ponto: RegistroPonto):
        ponto_model = RegistroFromSchemaFactory(ponto).create()

        try:
            self.db.add(ponto_model)
            self.db.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Dados inválidos!'
            )

    def _resolve_tipo_entrada_saida(self, cpf: str, data: str, count_cache: dict) -> str:
        cache_key = f"{cpf}_{data}"
        if cache_key not in count_cache:
            count_cache[cache_key] = self.db.query(Registro_models).filter(
                Registro_models.cpf_funcionario == cpf,
                Registro_models.data == data,
            ).count()
        count_registros = count_cache[cache_key]
        is_entrada = (count_registros % 2) == 0
        count_cache[cache_key] += 1
        return "E" if is_entrada else "S"

    def sync_registers(
        self,
        registers: list[dict],
        empresa_id: int = 1,
        relogio_id: int = 1,
    ):
        registers_list: list[Registro_models] = []
        count_cache: dict[str, int] = {}

        try:
            for register in registers:
                adapter = RepRegistroAdapter(register)
                tipo = self._resolve_tipo_entrada_saida(
                    adapter.cpf, adapter.data, count_cache
                )
                register_on_db = RegistroFromRepFactory(
                    adapter, empresa_id, relogio_id, tipo
                ).create()
                registers_list.append(register_on_db)

            self.db.add_all(registers_list)
            self.db.commit()
        except ValidationError as e:
            print(e)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de integridade: {e}",
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def _format_registro(self, r: Registro_models) -> dict:
        try:
            funcionario = FuncionarioRepo(self.db).get_funcionario_by_cpf(
                r.cpf_funcionario, r.empresa_id
            )
            nome = funcionario.nome
        except HTTPException:
            nome = "Funcionário não encontrado"

        return {
            "nsr": r.nsr,
            "cpf_funcionario": r.cpf_funcionario,
            "funcionario": nome,
            "empresa_id": r.empresa_id,
            "relogio_id": r.relogio_id,
            "data": str(r.data),
            "hora": str(r.hora),
            "tipo": r.tipo,
        }

    def get_registros_por_funcionario(self, cpf: str) -> List[dict]:
        cpf_formatado = cpf.zfill(11) if len(cpf) < 11 else cpf

        registros = self.db.query(Registro_models).filter(
            Registro_models.cpf_funcionario == cpf_formatado
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        return [self._format_registro(r) for r in registros]

    def get_registros_por_data(self, data: str) -> List[dict]:
        registros = self.db.query(Registro_models).filter(
            Registro_models.data == data
        ).order_by(Registro_models.hora).all()

        return [self._format_registro(r) for r in registros]

    def get_registros_por_periodo(self, data_inicio: str, data_fim: str) -> List[dict]:
        registros = self.db.query(Registro_models).filter(
            Registro_models.data >= data_inicio,
            Registro_models.data <= data_fim,
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        return [self._format_registro(r) for r in registros]

    def get_registros_por_funcionario_periodo(
        self, cpf: str, data_inicio: str, data_fim: str
    ) -> List[dict]:
        cpf_formatado = cpf.zfill(11) if len(cpf) < 11 else cpf

        registros = self.db.query(Registro_models).filter(
            Registro_models.cpf_funcionario == cpf_formatado,
            Registro_models.data >= data_inicio,
            Registro_models.data <= data_fim,
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        return [self._format_registro(r) for r in registros]
