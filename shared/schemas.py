from pydantic import BaseModel
from typing import Optional, Dict, Any

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
