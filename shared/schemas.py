from pydantic import BaseModel, Field 
from typing import Optional, Dict, Any 

from enum import Enum

class RedacaoStatusEnum(str, Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDO = "CONCLUIDO"
    ERRO = "ERRO"


class RedacaoCreate(BaseModel):
    tema: str
    texto_redacao: str


class UserCreate(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int
    email: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class RedacaoStatus(BaseModel):
    id: int
    status: RedacaoStatusEnum
    message: str


class RedacaoResult(BaseModel):
    id: int
    status: RedacaoStatusEnum
    tema: str
    resultado_json: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class AvaliacaoCompetencia(BaseModel):
    competencia: int = Field(description="O número da competência (de 1 a 5)")
    analise_critica: str = Field(description="Análise detalhada dos erros encontrados e raciocínio antes da nota.")
    nota: int = Field(description="A nota para esta competência (0, 40, 80, 120, 160, ou 200)")
    justificativa: str = Field(description="A justificativa final resumida para a nota atribuída.")