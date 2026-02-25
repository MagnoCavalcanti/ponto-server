from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from re import compile

class RegistroPonto(BaseModel):

    cpf_funcionario: str = Field(..., description="CPF do funcionário que registrou o ponto")
    empresa_id: int = Field(..., description="Identificador da empresa ao qual o funcionário faz parte")
    relogio_id: int = Field(..., description="Identificador do relógio que o registro foi importado")
    data: date = Field(..., description="Data do registro")
    hora: time = Field(..., description="Horário exato do registro")
    tipo: str = Field(..., description="Tipo do registro")


    @field_validator("tipo")
    def validar_tipo(cls, valor):
        if not compile(r"^(E|S)$").match(valor):
            raise ValueError("O tipo deve ser 'E' (entrada) ou 'S' (saída).")
        return valor
    class Config:
        orm_mode = True
    
    
