from decouple import config
from passlib.context import CryptContext

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.database.db_connection import Session as sessionmaker
from backend.models import UserModel




pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_db_session():
    try:
        session = sessionmaker()
        yield session
    finally:
        session.close()  

def create_superuser():
    """Cria o superusuário da plataforma se não existir"""
    session = sessionmaker()
    try:
        # Verifica se já existe
        existing = session.query(UserModel).filter_by(is_admin=True).first()
        if existing:
            print(f"✓ Superuser já existe: {existing.username}")
            return
        
        # Dados do superuser (coloque no .env)
        username = config("SUPERUSER_USERNAME", default="superadmin")
        password = config("SUPERUSER_PASSWORD", default="admin123")
        
        hashed_password = pwd_context.hash(password)
        
        superuser = UserModel(
            username=username,
            password=hashed_password,
            is_admin=True,
            empresa_id=None  # Superuser não pertence a empresa
        )
        
        session.add(superuser)
        session.commit()
        print(f"✓ Superuser criado: {username}")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Erro ao criar superuser: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_superuser()