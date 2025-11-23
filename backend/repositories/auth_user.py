from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import status, HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from decouple import config
from datetime import datetime, timedelta, timezone

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.schemas import User
from backend.models import UserModel

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
crypt_context = CryptContext(schemes=['sha256_crypt'])

class UserUseCases:

    def __init__(self, dbsession: Session):
        
        self.dbsession = dbsession #Recebe a Session da conexão do banco de dados 
        
    

    def register_user(self, user: User, empresa_id: int):
        user_model = UserModel(
            username= user.username,
            password= crypt_context.hash(user.password),
            empresa_id= empresa_id
        )
        try:
            self.dbsession.add(user_model)
            self.dbsession.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Usuário já existente!'
            )
        
    def login_user(self, empresa_id: int, user: User, expira_em: int = 30):
        user_db = self.dbsession.query(UserModel).filter_by(username=user.username, empresa_id=empresa_id).first()

        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Login inválido!'
            )
        
        if not crypt_context.verify(user.password, user_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Login inválido!'
            )
        
        exp = datetime.now(timezone.utc) + timedelta(minutes=expira_em)
        
        payload = {
            "sub": f"{user_db.username}: {user_db.empresa_id}",
            "exp": exp
        }

        token_de_acesso = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token_de_acesso,  # Mudança para "access_token"
            "token_type": "bearer",          # Adicionando "token_type"
            "exp": exp.isoformat("T")        # Adicionando "exp"
        }
    
    def login_superuser(self, user: User, expira_em: int = 30):
        user_db = self.dbsession.query(UserModel).filter_by(username=user.username, is_admin=True).first()

        print(user_db.empresa_id)

        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Login inválido!'
            )
        
        if not crypt_context.verify(user.password, user_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Login inválido!'
            )
        
        exp = datetime.now(timezone.utc) + timedelta(minutes=expira_em)
        
        payload = {
            "sub": f"superuser:{user_db.username}",
            "exp": exp
        }

        token_de_acesso = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token_de_acesso,
            "token_type": "bearer",
            "exp": exp.isoformat("T")
        }
    
    def verify_token_superuser(self, token: str):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = data['sub'].split(':')[1]
            user_on_db = self.dbsession.query(UserModel).filter_by(username=username, is_admin=True).first()

            if user_on_db is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token inválido'
                )
            return data
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido'
            )
        
    def verify_token(self, token: str):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = data['sub'].split(':')[0]
            user_on_db = self.dbsession.query(UserModel).filter_by(username=username).first()

            if user_on_db is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token inválido'
                )
            return data
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido'
            )