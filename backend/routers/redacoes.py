from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from shared import models, schemas
from shared.schemas import RedacaoStatusEnum
from backend.core.database import get_db
from backend.routers.auth import get_current_user
from backend.celery_app import celery_app

router = APIRouter(
    prefix="/api/v1/redacoes",
    tags=["Redacoes"],
)

@router.post(
    "/",
    response_model=schemas.RedacaoStatus,
    status_code=202,
    summary="Submeter uma redação para correção",
)
def criar_correcao(
    redacao: schemas.RedacaoCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_redacao = models.Redacao(
        tema=redacao.tema, 
        texto_redacao=redacao.texto_redacao, 
        status=RedacaoStatusEnum.PENDENTE,
        user_id=current_user.id
    )
    db.add(db_redacao)
    db.commit()
    db.refresh(db_redacao)

    celery_app.send_task("correct_essay", args=[db_redacao.id])

    return {
        "id": db_redacao.id,
        "status": RedacaoStatusEnum.PENDENTE,
        "message": "Sua redação foi recebida e está na fila para correção.",
    }


@router.get(
    "/",
    response_model=List[schemas.RedacaoResult],
    summary="Listar todas as redações do usuário logado",
)
def listar_minhas_redacoes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Redacao).filter(models.Redacao.user_id == current_user.id).all()


@router.get(
    "/{redacao_id}",
    response_model=schemas.RedacaoResult,
    summary="Obter o status e resultado de uma correção",
)
def obter_status_correcao(
    redacao_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Garante que o usuário só veja SUAS próprias redações
    db_redacao = (
        db.query(models.Redacao)
        .filter(models.Redacao.id == redacao_id, models.Redacao.user_id == current_user.id)
        .first()
    )
    if db_redacao is None:
        raise HTTPException(status_code=404, detail="Redação não encontrada")
    return db_redacao
