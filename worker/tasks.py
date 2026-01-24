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
    Usa um único Event Loop para evitar erros de 'Loop Closed' com clientes HTTP.
    """
    
    # Função interna assíncrona que contém toda a lógica
    async def _fluxo_correcao_async():
        db: Session = SessionLocal()
        redacao = None
        try:
            from shared.schemas import RedacaoStatusEnum
            
            # nonlocal para acessar argumentos da func externa (opcional, mas explicito)
            # Na verdade, como é closure, acessa direto.
            
            nonlocal correcao_1_json, correcao_2_json, correcao_supervisor_json
            
            # Recarrega JSONs se existirem (para retry)
            c1 = json.loads(correcao_1_json) if correcao_1_json else None
            c2 = json.loads(correcao_2_json) if correcao_2_json else None
            c3 = json.loads(correcao_supervisor_json) if correcao_supervisor_json else None

            redacao = db.query(Redacao).filter(Redacao.id == redacao_id).first()
            if not redacao:
                print(f"Erro: Redação com ID {redacao_id} não encontrada.")
                return

            print(f"Iniciando correção da redação ID: {redacao_id}")
            redacao.status = RedacaoStatusEnum.PROCESSANDO
            db.commit()

            # --- Corretores 1 e 2 (Paralelo) ---
            async def _run_c1():
                if c1:
                     print("Pulando Corretor 1 (já existe).")
                     return c1
                print("Executando Corretor 1...")
                return await executar_correcao_completa_async("Corretor 1", redacao.texto_redacao, redacao.tema)

            async def _run_c2():
                if c2:
                     print("Pulando Corretor 2 (já existe).")
                     return c2
                print("Executando Corretor 2...")
                return await executar_correcao_completa_async("Corretor 2", redacao.texto_redacao, redacao.tema)

            c1, c2 = await asyncio.gather(_run_c1(), _run_c2())

            # --- Verificação ---
            if not verificar_discrepancia(c1, c2):
                resultado_final = calcular_nota_consolidada(c1, c2)
            else:
                # --- Supervisor ---
                if not c3:
                    print("Discrepância detectada. Executando Supervisor...")
                    c3 = await executar_correcao_completa_async(
                        "Corretor Supervisor", redacao.texto_redacao, redacao.tema
                    )
                    print("Corretor Supervisor finalizado (async).")
                else:
                    print("Pulando Supervisor (já existe).")

                resultado_final = resolver_discrepancia_com_supervisor(c1, c2, c3)

            # Salva
            redacao.resultado_json = resultado_final
            redacao.status = RedacaoStatusEnum.CONCLUIDO
            db.commit()
            print(f"Correção da redação ID: {redacao_id} finalizada com sucesso.")

        except Exception as e:
            db.rollback()
            print(f"Erro fatal na Task: {e}")
            if redacao:
                redacao.status = RedacaoStatusEnum.ERRO
                redacao.message = str(e)
                try:
                    db.commit()
                except:
                    pass
        finally:
            db.close()

    # Executa tudo em UM único loop
    # Isso garante que o httpx tenha tempo de abrir e fechar conexões dentro do mesmo loop
    asyncio.run(_fluxo_correcao_async())


