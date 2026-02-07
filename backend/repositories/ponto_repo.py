from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import status, HTTPException
from pydantic import ValidationError
from datetime import datetime
from typing import List


import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.schemas import RegistroPonto
from backend.models import RegistroPonto as Registro_models
from .funcionario_repo import FuncionarioRepo

class PontoRepo:

    def __init__(self, dbsession: Session):
        self.db = dbsession

    def Bater_Ponto(self, ponto: RegistroPonto):
        ponto_model = Registro_models(
            **ponto.model_dump(exclude_unset=True)
        )

        try:
            self.db.add(ponto_model)
            self.db.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Dados inválidos!'
            )
        
    def sync_registers(self, registers: list[dict]):
        registers_list: list[Registro_models] = []
        # Dicionário para rastrear contagens por funcionário/dia durante a sincronização
        count_cache = {}
        
        try:
            for register in registers:
                data, hora = register["data"].split(" ")
                
                # Adiciona segundos se não estiver presente
                if hora.count(':') == 1:
                    hora = f"{hora}:00"
                
                # Converte data de DD/MM/YYYY para YYYY-MM-DD
                data_obj = datetime.strptime(data, "%d/%m/%Y")
                data_formatada = data_obj.strftime("%Y-%m-%d")
                
                # Formata o CPF antes de usar nas queries
                cpf = str(register["cpf"])
                
    
                if len(cpf) < 11:
                    cpf = cpf.zfill(11)
    
                
                # Chave para identificar funcionário/dia
                cache_key = f"{cpf}_{data_formatada}"
                
                # Se ainda não contou para este funcionário/dia, busca do banco
                if cache_key not in count_cache:
                    count_cache[cache_key] = self.db.query(Registro_models).filter(
                        Registro_models.cpf_funcionario == cpf,
                        Registro_models.data == data_formatada
                    ).count()

                # Pega a contagem atual (banco + registros já processados nesta batch)
                count_registros = count_cache[cache_key]

                # Se o número de registros é par, a próxima batida é entrada (ímpar: 1, 3, 5...)
                # Se o número de registros é ímpar, a próxima batida é saída (par: 2, 4, 6...)
                is_entrada = (count_registros % 2) == 0


                #falta adicionar empresa_id e relogio_id, preciso abrir espaço na lógica pra isso
                print(cpf)
                register_on_db = Registro_models(
                    nsr = register["nsr"],
                    cpf_funcionario = cpf,
                    empresa_id = 1,
                    relogio_id = 1,
                    data = data_formatada,
                    hora = hora,
                    tipo = "E" if is_entrada else "S"
                )

                registers_list.append(register_on_db)
                
                # Incrementa o contador para próximas iterações
                count_cache[cache_key] += 1
            
            self.db.add_all(registers_list)
            self.db.commit()
        except ValidationError as e:
            print(e)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de integridade: {e}"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    def get_registros_por_funcionario(self, cpf: str) -> List[Registro_models]:
        """
        Retorna todos os registros de ponto de um funcionário específico.
        
        Args:
            cpf: CPF do funcionário
            
        Returns:
            Lista de registros do funcionário
        """
        cpf_formatado = cpf.zfill(11) if len(cpf) < 11 else cpf
        
        registros = self.db.query(Registro_models).filter(
            Registro_models.cpf_funcionario == cpf_formatado
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        registros_formatados = []

        for r in registros:
            funcionario = FuncionarioRepo(self.db).get_funcionario_by_cpf(r.cpf_funcionario, r.empresa_id)
            funcionario = funcionario.nome if funcionario else "Funcionário não encontrado"

            registros_formatados.append({
                    "nsr": r.nsr,
                    "cpf_funcionario": r.cpf_funcionario,
                    "funcionario": funcionario,
                    "empresa_id": r.empresa_id,
                    "relogio_id": r.relogio_id,
                    "data": str(r.data),
                    "hora": str(r.hora),
                    "tipo": r.tipo
            })
        
        return registros_formatados

    def get_registros_por_data(self, data: str) -> List[Registro_models]:
        """
        Retorna todos os registros de ponto de uma data específica.
        
        Args:
            data: Data no formato YYYY-MM-DD
            
        Returns:
            Lista de registros da data
        """
        registros = self.db.query(Registro_models).filter(
            Registro_models.data == data
        ).order_by(Registro_models.hora).all()

        registros_formatados = []

        for r in registros:
            funcionario = FuncionarioRepo(self.db).get_funcionario_by_cpf(r.cpf_funcionario, r.empresa_id)
            funcionario = funcionario.nome if funcionario else "Funcionário não encontrado"

            registros_formatados.append({
                    "nsr": r.nsr,
                    "cpf_funcionario": r.cpf_funcionario,
                    "funcionario": funcionario,
                    "empresa_id": r.empresa_id,
                    "relogio_id": r.relogio_id,
                    "data": str(r.data),
                    "hora": str(r.hora),
                    "tipo": r.tipo
            })
        
        return registros_formatados

    def get_registros_por_periodo(self, data_inicio: str, data_fim: str) -> List[Registro_models]:
        """
        Retorna todos os registros de ponto em um período.
        
        Args:
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
            
        Returns:
            Lista de registros no período
        """
        registros = self.db.query(Registro_models).filter(
            Registro_models.data >= data_inicio,
            Registro_models.data <= data_fim
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        registros_formatados = []

        for r in registros:
            funcionario = FuncionarioRepo(self.db).get_funcionario_by_cpf(r.cpf_funcionario, r.empresa_id)
            funcionario = funcionario.nome if funcionario else "Funcionário não encontrado"

            registros_formatados.append({
                    "nsr": r.nsr,
                    "cpf_funcionario": r.cpf_funcionario,
                    "funcionario": funcionario,
                    "empresa_id": r.empresa_id,
                    "relogio_id": r.relogio_id,
                    "data": str(r.data),
                    "hora": str(r.hora),
                    "tipo": r.tipo
            })
        
        return registros_formatados

    def get_registros_por_funcionario_periodo(self, cpf: str, data_inicio: str, data_fim: str) -> List[Registro_models]:
        """
        Retorna todos os registros de ponto de um funcionário em um período específico.
        
        Args:
            cpf: CPF do funcionário
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
            
        Returns:
            Lista de registros do funcionário no período
        """
        cpf_formatado = cpf.zfill(11) if len(cpf) < 11 else cpf
        
        registros = self.db.query(Registro_models).filter(
            Registro_models.cpf_funcionario == cpf_formatado,
            Registro_models.data >= data_inicio,
            Registro_models.data <= data_fim
        ).order_by(Registro_models.data.desc(), Registro_models.hora.desc()).all()

        registros_formatados = []

        for r in registros:
            funcionario = FuncionarioRepo(self.db).get_funcionario_by_cpf(r.cpf_funcionario, r.empresa_id)
            funcionario = funcionario.nome if funcionario else "Funcionário não encontrado"

            registros_formatados.append({
                    "nsr": r.nsr,
                    "cpf_funcionario": r.cpf_funcionario,
                    "funcionario": funcionario,
                    "empresa_id": r.empresa_id,
                    "relogio_id": r.relogio_id,
                    "data": str(r.data),
                    "hora": str(r.hora),
                    "tipo": r.tipo
            })
        
        return registros_formatados 