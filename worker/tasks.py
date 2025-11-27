import json
import asyncio
import re
import math
import time
from sqlalchemy.orm import Session
from google.api_core.exceptions import ResourceExhausted

from celery_app import celery_app
from shared.models import SessionLocal, Redacao
from agents.core import executar_correcao_completa_async
from banca.rules import (
    verificar_discrepancia,
    calcular_nota_consolidada,
    resolver_discrepancia_com_supervisor,
)


@celery_app.task(name="correct_essay", bind=True)
def correct_essay(
    self,
    redacao_id: int,
    correcao_1_json: str = None,
    correcao_2_json: str = None,
    correcao_supervisor_json: str = None,
):
    """
    Ponto de entrada orquestrado para a tarefa de correção em background.
    """
    db: Session = SessionLocal()
    redacao = None

    c1 = json.loads(correcao_1_json) if correcao_1_json else None
    c2 = json.loads(correcao_2_json) if correcao_2_json else None
    c3 = json.loads(correcao_supervisor_json) if correcao_supervisor_json else None

    try:
        redacao = db.query(Redacao).filter(Redacao.id == redacao_id).first()
        if not redacao:
            print(f"Erro: Redação com ID {redacao_id} não encontrada.")
            return

        print(f"Iniciando correção da redação ID: {redacao_id}")
        redacao.status = "PROCESSANDO"
        db.commit()

        if not c1:
            print("Executando Corretor 1...")

            c1 = asyncio.run(
                executar_correcao_completa_async(
                    "Corretor 1", redacao.texto_redacao, redacao.tema
                )
            )
            print("Corretor 1 finalizado. Pausando...")
            time.sleep(15)
        else:
            print("Pulando Corretor 1 (resultado já existe do retry).")

        if not c2:
            print("Executando Corretor 2...")

            c2 = asyncio.run(
                executar_correcao_completa_async(
                    "Corretor 2", redacao.texto_redacao, redacao.tema
                )
            )
            print("Corretor 2 finalizado.")
        else:
            print("Pulando Corretor 2 (resultado já existe do retry).")

        if not verificar_discrepancia(c1, c2):
            resultado_final = calcular_nota_consolidada(c1, c2)
        else:
            if not c3:
                print(
                    "Discrepância detectada. Pausando e executando Corretor Supervisor..."
                )
                time.sleep(15)

                c3 = asyncio.run(
                    executar_correcao_completa_async(
                        "Corretor Supervisor", redacao.texto_redacao, redacao.tema
                    )
                )
                print("Corretor Supervisor finalizado.")
            else:
                print("Pulando Corretor Supervisor (resultado já existe do retry).")

            resultado_final = resolver_discrepancia_com_supervisor(c1, c2, c3)

        redacao.resultado_json = resultado_final
        redacao.status = "CONCLUIDO"
        db.commit()
        print(f"Correção da redação ID: {redacao_id} finalizada com sucesso.")

    except ResourceExhausted as e:
        db.rollback()
        print(f"Erro de Limite de Taxa (429) detectado: {e}")

        countdown_seconds = 60
        try:
            match = re.search(r"Please retry in (\d+\.?\d*)", str(e))
            if match:
                wait_time = float(match.group(1))
                countdown_seconds = math.ceil(wait_time) + 1
                print(
                    f"API sugeriu esperar {wait_time}s. Reagendando em {countdown_seconds}s."
                )
            else:
                print(
                    f"Não foi possível extrair o tempo de espera. Usando padrão de {countdown_seconds}s."
                )
        except Exception as re_e:
            print(f"Erro ao extrair tempo de espera: {re_e}. Usando padrão de 60s.")

        raise self.retry(
            exc=e,
            countdown=countdown_seconds,
            max_retries=5,
            args=[],
            kwargs={
                "redacao_id": redacao_id,
                "correcao_1_json": json.dumps(c1) if c1 else None,
                "correcao_2_json": json.dumps(c2) if c2 else None,
                "correcao_supervisor_json": json.dumps(c3) if c3 else None,
            },
        )

    except Exception as e:
        db.rollback()
        if redacao:
            redacao.status = "ERRO"
            redacao.resultado_json = {"erro": str(e)}
            db.commit()
        print(f"Erro GERAL ao corrigir redação ID {redacao_id}: {e}")
    finally:
        db.close()
