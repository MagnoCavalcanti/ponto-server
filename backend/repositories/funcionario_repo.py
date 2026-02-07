from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import status, HTTPException
from datetime import datetime

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.schemas import Funcionario, DictDesktop
from backend.models import Funcionario as Funcionario_models

class FuncionarioRepo:

    def __init__(self, dbsession: Session):
        self.db = dbsession

    
    def register_funcionario(self, funcionario:Funcionario, empresa_id: int):
        if funcionario.cpf == 'XXX.XXX.XXX-XX':
            funcionario.cpf = None # Não pode ser None
            
        funcionario_model = Funcionario_models(
            **funcionario.__dict__
        )
        if funcionario.empresa_id != empresa_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada!"
            )
        
        try:
            self.db.add(funcionario_model)
            self.db.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    def list_funcionario(self, empresa_id: int):
        try:
            funcionario_db = self.db.query(Funcionario_models).filter_by(empresa_id=empresa_id).all()
            
            return funcionario_db
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro no servidor!"
            )
        
    def update_funcionario(self, id_funcionario: int, value_update, empresa_id: int):
        try:
            updated = self.db.query(Funcionario_models).filter(Funcionario_models.id ==id_funcionario, Funcionario_models.empresa_id == empresa_id).update(value_update)
            self.db.commit()
            if updated == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Funcionário não encontrado!"
                )
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha na atualização! Verifique se os dados são válidos."
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}"
            )

    def get_funcionario_by_cpf(self, cpf: str, empresa_id: int):
        try:
            funcionario_db = (
                self.db.query(Funcionario_models)
                .filter(Funcionario_models.cpf == cpf, Funcionario_models.empresa_id == empresa_id)
                .first()
            )
            if not funcionario_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Funcionário não encontrado!"
                )
            return funcionario_db
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro no servidor!"
            )

    def bulk_insert_funcionario(self, list_funcionarios: list[dict], empresa_id: int):
        funcionarios_db = []
        for funcionario in list_funcionarios:
            # valida se o funcionário pertence à mesma empresa
            if funcionario['empresa_id'] != empresa_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empresa não encontrada para um dos funcionários!"
                )
            # normaliza CPF (opcional)
            if funcionario['cpf'] == "XXX.XXX.XXX-XX":
                funcionario.cpf = None

            funcionario_db = Funcionario_models(
                **funcionario
            )
            funcionarios_db.append(funcionario_db)

        try:
            # add_all preserva comportamento ORM (relacionamentos, eventos)
            self.db.add_all(funcionarios_db)
            self.db.commit()
            
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