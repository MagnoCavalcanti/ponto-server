from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.repositories import UserUseCases, EmpresaRepositorio
from backend.database.seed_data import get_db_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/login")  # Define o esquema de autenticação

def verificar_empresa(empresa: str, db: Session = Depends(get_db_session)):
    empresa_repo = EmpresaRepositorio(db)
    empresa_id = empresa_repo.get_empresa_by_name(empresa_nome=empresa)
    return empresa_id

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token
        uc = UserUseCases(dbsession=db)
        payload = uc.verify_token(token)
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise credentials_exception
    
def get_current_superuser(token : str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token
        uc = UserUseCases(dbsession=db)
        payload = uc.verify_token_superuser(token)
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise credentials_exception
    