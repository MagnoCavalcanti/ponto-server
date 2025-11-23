from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.repositories import EmpresaRepositorio
from backend.database.seed_data import get_db_session
from backend.schemas import Empresa
from backend.services import verificar_empresa

empresa_router = APIRouter(prefix="/empresas")



@empresa_router.get("/")
def listar_empresas(db: Session = Depends(get_db_session)):
    empresa_repo = EmpresaRepositorio(db_session=db)
    empresas = empresa_repo.read_empresa()

    return empresas

@empresa_router.get("/{empresa}")
def verificar_id_empresa(empresa: str, db: Session = Depends(get_db_session)):
    id_empresa = verificar_empresa(empresa, db)
    return {"id_empresa": id_empresa, "empresa": empresa, "msg": "sucess"}


@empresa_router.put("/atualizar/{id}")
def atualizar_empresa(id:int, empresa: Empresa, db: Session = Depends(get_db_session)):
    empresa_repo = EmpresaRepositorio(db_session=db)
    empresa_repo.update_empresa(
        id_empresa=id,
        value_update= {
            "nome": empresa.nome,
            "cnpj": empresa.cnpj
                        }
    )

    return JSONResponse(
        content={'msg': 'success'},
        status_code=status.HTTP_201_CREATED
    )