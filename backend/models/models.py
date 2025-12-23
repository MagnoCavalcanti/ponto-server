from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates
from datetime import datetime
import re


from .base import Base



class UserModel(Base):

    __tablename__ = 'users'
    id = Column('id',Integer, autoincrement=True, primary_key=True)
    username = Column('username', String, nullable=False)
    password = Column('password', String, nullable=False)
    is_admin = Column('is_admin', Boolean, default=False)
    empresa_id = Column('empresa_id', Integer, ForeignKey("empresas.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint('empresa_id', 'username', name='uq_user_empresa'),
    )



class Funcionario(Base):

    __tablename__ = "funcionarios"
    id = Column(Integer, autoincrement=True, primary_key=True)
    nome= Column(String, nullable=False)
    matricula= Column(Integer, nullable=False, unique=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    funcao= Column(String)
    grupo= Column(String)
    cpf= Column(String, nullable=False, unique=True)  

    @validates('cpf')
    def validate_cpf(self, key, cpf):
        # Regex para validar CPF formatado ou apenas números
        pattern = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"

        if not re.match(pattern, cpf):
            raise ValueError("CPF inválido. Use o formato XXX.XXX.XXX-XX.")
        
        return cpf
   


class Empresa(Base):

    __tablename__ = "empresas"
    id = Column(Integer, autoincrement=True, primary_key=True)
    nome = Column(String, nullable=False, unique=True)
    cnpj = Column(String, nullable=False, unique=True)

    
    @validates('cnpj')
    def validate_cnpj(self, key, cnpj):
        # Regex para validar CNPJ formatado ou apenas números
            pattern = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"

            if not re.match(pattern, cnpj):
                raise ValueError("CNPJ inválido. Use o formato XX.XXX.XXX/XXXX-XX.")

            return cnpj

class RegistroPonto(Base):

    __tablename__= "registros"
    nsr = Column(Integer, autoincrement=True, primary_key=True)
    cpf_funcionario = Column(String, ForeignKey("funcionarios.cpf"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)  
    relogio_id = Column(Integer, ForeignKey("relogios.id"), nullable=False)  
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    tipo = Column(String, Enum("Entrada", "Saída", name="tipo_registro"), nullable=False)

    __table_args__ = (
        UniqueConstraint('relogio_id', 'nsr', name='unique_device_nsr'),
    )


    @validates("data")
    def validate_data(self, key, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

    @validates("hora")
    def validate_hora(self, key, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%H:%M:%S").time()
        return value
    

class Relogio(Base):
    __tablename__ = "relogios"
    id = Column(Integer, autoincrement=True, primary_key=True)
    nome = Column(String, nullable=False, unique=True)
    user = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    ip = Column(String, nullable=False, unique=True)
    porta = Column(Integer, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    __table_args__ = (
        CheckConstraint('porta >= 0 AND porta <= 65535', name='porta_range'),
    ) 

    @validates('porta')
    def validate_porta(self, key, value):
        if value < 0 or value > 65535:
            raise ValueError('Porta inválida')
        return value

    
    