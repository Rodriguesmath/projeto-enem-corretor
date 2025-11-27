from pydantic import BaseModel, Field 
from typing import Optional, Dict, Any, List 


class RedacaoCreate(BaseModel):
    tema: str
    texto_redacao: str


class RedacaoStatus(BaseModel):
    id: int
    status: str
    message: str


class RedacaoResult(BaseModel):
    id: int
    status: str
    tema: str
    resultado_json: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True

class AvaliacaoCompetencia(BaseModel):
    competencia: int = Field(description="O número da competência (de 1 a 5)")
    analise_critica: str = Field(description="Análise detalhada dos erros encontrados e raciocínio antes da nota.")
    nota: int = Field(description="A nota para esta competência (0, 40, 80, 120, 160, ou 200)")
    justificativa: str = Field(description="A justificativa final resumida para a nota atribuída.")