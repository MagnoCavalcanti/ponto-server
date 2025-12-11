from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.schemas import User, Empresa
from backend.database.seed_data import get_db_session
from backend.repositories import UserUseCases, EmpresaRepositorio
from backend.services import get_current_user, verificar_empresa, get_current_superuser

auth_router = APIRouter(prefix='/auth')

@auth_router.post('/cadastro')
def RegistrarUsuario(empresa: Empresa, user: User, db: Session = Depends(get_db_session), current_user: dict = Depends(get_current_superuser)):

    empresa_uc = EmpresaRepositorio(db)
    empresa_id = empresa_uc.register_empresa(empresa=empresa)
    register = UserUseCases(dbsession=db)
    register.register_user(user= user, empresa_id=empresa_id)
    return JSONResponse(
        content={'msg': 'success'},
        status_code=status.HTTP_201_CREATED
    )

@auth_router.post("/{empresa}/login")
def LoginUsuario(
    empresa: str,
    request_form_user: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db_session)
    ):
    empresa_id = verificar_empresa(empresa, db)
    login = UserUseCases(dbsession=db)
    user = User(
        username=request_form_user.username,
        password=request_form_user.password,
    )

    data_auth = login.login_user(empresa_id=empresa_id, user=user)

    return JSONResponse(
        content=data_auth,
        status_code=status.HTTP_200_OK
    )

@auth_router.post("/superuser")
def LoginSuperuser(
    request_form_user: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db_session)
    ):
    login = UserUseCases(dbsession=db)
    user = User(
        username=request_form_user.username,
        password=request_form_user.password,
    )

    data_auth = login.login_superuser(user=user)

    return JSONResponse(
        content=data_auth,
        status_code=status.HTTP_200_OK
    )

@auth_router.get("/verify-token")
def verify_token(current_user: dict = Depends(get_current_user)):
    try:
        return {"message": "Token is valid", "user": current_user}
    except Exception as e:
        return JSONResponse(
            content={"error": "Invalid token"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
@auth_router.get("/protected-route")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "You are authenticated", "user": current_user}
    

    
        