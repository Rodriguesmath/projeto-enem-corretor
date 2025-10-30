from fastapi import FastAPI, Depends, HTTPException
# 1. Importar o CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from shared import models, schemas
from database import get_db
from celery_app import celery_app

app = FastAPI(title="API de Correção de Redação ENEM", version="1.0.0")

# 2. Adicionar o Middleware de CORS
# Isso deve vir antes da definição das suas rotas.

# Lista de origens permitidas.
# Para desenvolvimento, usar ["*"] permite que qualquer front-end
# (como seu index.html aberto localmente) acesse a API.
origins = [
    "*", # Permite todas as origens (fácil para testes locais)
    # Em produção, você mudaria para:
    # "https://seusite.com",
    # "http://127.0.0.1:5500" # Se estiver usando o Live Server do VS Code
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Quais origens podem fazer requisições
    allow_credentials=True,    # Permite cookies (se você usar)
    allow_methods=["*"],       # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],       # Permite todos os cabeçalhos
)

# --- Fim da adição do CORS ---


@app.get("/", summary="Endpoint raiz da API")
def read_root():
    return {"message": "API de Correção de Redações do ENEM no ar!"}

@app.post("/api/v1/redacoes/", response_model=schemas.RedacaoStatus, status_code=202, summary="Submeter uma redação para correção")
def criar_correcao(redacao: schemas.RedacaoCreate, db: Session = Depends(get_db)):
    db_redacao = models.Redacao(
        tema=redacao.tema,
        texto_redacao=redacao.texto_redacao,
        status="PENDENTE"
    )
    db.add(db_redacao)
    db.commit()
    db.refresh(db_redacao)

    celery_app.send_task("correct_essay", args=[db_redacao.id])

    return {
        "id": db_redacao.id,
        "status": "PENDENTE",
        "message": "Sua redação foi recebida e está na fila para correção."
    }

@app.get("/api/v1/redacoes/{redacao_id}", response_model=schemas.RedacaoResult, summary="Obter o status e resultado de uma correção")
def obter_status_correcao(redacao_id: int, db: Session = Depends(get_db)):
    db_redacao = db.query(models.Redacao).filter(models.Redacao.id == redacao_id).first()
    if db_redacao is None:
        raise HTTPException(status_code=404, detail="Redação não encontrada")
    return db_redacao
