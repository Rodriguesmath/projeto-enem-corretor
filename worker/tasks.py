# Importações Padrão
import os
import json
import asyncio
from celery import Celery
from sqlalchemy.orm import Session
from shared.models import SessionLocal, Redacao

# Importações do LangChain e Google
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any

# Configuração do Celery App
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)
celery_app.conf.update(task_routes={'tasks.correct_essay': {'queue': 'correcoes'}})

# --- Modelos Pydantic para a Estrutura de Saída ---
class AvaliacaoCompetencia(BaseModel):
    competencia: int = Field(description="O número da competência (de 1 a 5)")
    nota: int = Field(description="A nota para esta competência (0, 40, 80, 120, 160, ou 200)")
    justificativa: str = Field(description="A explicação detalhada para a nota atribuída.")

class CorrecaoCompleta(BaseModel):
    competencias: List[AvaliacaoCompetencia]
    nota_final: int = Field(description="A soma das notas das cinco competências.")
    comentarios_gerais: str = Field(description="Um parágrafo com comentários gerais e sugestões.")

# --- Lógica Multiagente (5 Agentes por Corretor) ---

PROMPT_AGENTE_COMPETENCIA = ChatPromptTemplate.from_template(
    """Você é um corretor especialista do ENEM focado EXCLUSIVAMENTE na Competência {competencia_numero}.

    Sua única tarefa é analisar a redação a seguir e atribuir uma nota e justificativa apenas para a Competência {competencia_numero}.

    Critérios de Avaliação para a Competência {competencia_numero}:
    {criterios_competencia}

    Redação para Análise:
    ---
    {redacao}
    ---
    
    Tema da Redação: {tema}

    Instruções de Saída:
    Retorne sua análise estritamente no formato JSON a seguir. Não inclua nenhuma outra palavra ou comentário.
    {format_instructions}
    """
)

async def avaliar_competencia_async(llm: ChatGoogleGenerativeAI, texto_redacao: str, tema: str, comp_info: dict) -> dict:
    """
    Este é o "sub-agente". Ele foca em avaliar uma única competência.
    """
    parser = JsonOutputParser(pydantic_object=AvaliacaoCompetencia)
    chain = PROMPT_AGENTE_COMPETENCIA | llm | parser
    resultado = await chain.ainvoke({
        "competencia_numero": comp_info['numero'],
        "criterios_competencia": comp_info['criterios'],
        "redacao": texto_redacao,
        "tema": tema,
        "format_instructions": parser.get_format_instructions()
    })
    return resultado

async def executar_correcao_completa_async(id_corretor: str, texto_redacao: str, tema: str) -> Dict[str, Any]:
    """
    Esta função é o "Agente Corretor Orquestrador".
    Ele gerencia 5 sub-agentes (um para cada competência) em paralelo.
    """
    print(f"[{id_corretor}] Orquestrando 5 agentes de competência em paralelo...")
    
    temperatura = 0.4 if id_corretor == "Corretor 1" else 0.6
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=temperatura)

    competencias_info = [
        {'numero': 1, 'criterios': "Demonstrar domínio da modalidade escrita formal da Língua Portuguesa. Avalie desvios gramaticais e de convenções da escrita."},
        {'numero': 2, 'criterios': "Compreender a proposta e aplicar conceitos das áreas do conhecimento. Avalie o uso de repertório sociocultural e a estrutura dissertativo-argumentativa."},
        {'numero': 3, 'criterios': "Selecionar, relacionar, organizar e interpretar informações e argumentos. Avalie a coerência, o projeto de texto e a defesa do ponto de vista."},
        {'numero': 4, 'criterios': "Demonstrar conhecimento dos mecanismos linguísticos para a argumentação. Avalie o uso de conectivos e a coesão entre parágrafos e frases."},
        {'numero': 5, 'criterios': "Elaborar proposta de intervenção. Avalie os 5 elementos (ação, agente, modo/meio, efeito, detalhamento) e o respeito aos direitos humanos."}
    ]

    tasks = [avaliar_competencia_async(llm, texto_redacao, tema, info) for info in competencias_info]
    resultados_competencias = await asyncio.gather(*tasks)
    
    resultados_competencias.sort(key=lambda x: x['competencia'])

    nota_final_calculada = sum(r['nota'] for r in resultados_competencias)
    
    prompt_comentario = ChatPromptTemplate.from_template("Com base nestas 5 avaliações de competências de uma redação, escreva um parágrafo de comentário geral conciso e útil para o aluno. Avaliações: {avaliacoes}")
    chain_comentario = prompt_comentario | llm
    comentario_geral_obj = await chain_comentario.ainvoke({"avaliacoes": json.dumps(resultados_competencias)})
    comentario_geral = comentario_geral_obj.content

    correcao = {
        "competencias": resultados_competencias,
        "nota_final": nota_final_calculada,
        "comentarios_gerais": comentario_geral,
        "id_corretor": id_corretor
    }
    
    print(f"[{id_corretor}] Orquestração finalizada. Nota final: {nota_final_calculada}")
    return correcao

# --- Funções de Controle da Banca (Lógica ENEM Real) ---

def verificar_discrepancia(c1: Dict[str, Any], c2: Dict[str, Any]) -> bool:
    if abs(c1['nota_final'] - c2['nota_final']) > 100: 
        print(f"Discrepância TOTAL detectada: {c1['nota_final']} vs {c2['nota_final']}")
        return True
    for comp1, comp2 in zip(c1['competencias'], c2['competencias']):
        if abs(comp1['nota'] - comp2['nota']) > 80:
            print(f"Discrepância na Competência {comp1['competencia']} detectada: {comp1['nota']} vs {comp2['nota']}")
            return True
    return False

def calcular_nota_consolidada(c1: Dict[str, Any], c2: Dict[str, Any]) -> Dict[str, Any]:
    print("--- SEM DISCREPÂNCIA. Calculando média por competência. ---")
    
    correcao_final = {
        "competencias": [],
        "nota_final": 0,
        "fonte_resultado": "Média dos Corretores 1 e 2",
        "detalhes": [c1, c2]
    }

    for comp1, comp2 in zip(c1['competencias'], c2['competencias']):
        nota_media_comp = (comp1['nota'] + comp2['nota']) / 2
        
        correcao_final['competencias'].append({
            "competencia": comp1['competencia'],
            "nota": nota_media_comp,
            "justificativa": f"[Média C{comp1['competencia']}] Corretor 1 ({comp1['nota']}): {comp1['justificativa']} | Corretor 2 ({comp2['nota']}): {comp2['justificativa']}"
        })
    
    correcao_final['nota_final'] = sum(c['nota'] for c in correcao_final['competencias'])
    return correcao_final

def resolver_discrepancia_com_supervisor(c1: Dict[str, Any], c2: Dict[str, Any], c3: Dict[str, Any]) -> Dict[str, Any]:
    print("--- DISCREPÂNCIA DETECTADA! Resolvendo com base nas duas notas mais próximas por competência. ---")
    
    correcao_final = {
        "competencias": [],
        "nota_final": 0,
        "fonte_resultado": "Consenso da Banca (média das 2 notas mais próximas)",
        "detalhes": [c1, c2, c3]
    }

    for i in range(5):
        s1 = c1['competencias'][i]['nota']
        s2 = c2['competencias'][i]['nota']
        s3 = c3['competencias'][i]['nota']

        diff13 = abs(s1 - s3)
        diff23 = abs(s2 - s3)
        diff12 = abs(s1 - s2) # Menos provável de ser o menor, mas incluído para robustez

        nota_consenso = 0
        
        if diff13 <= diff12 and diff13 <= diff23:
            nota_consenso = (s1 + s3) / 2
        elif diff23 <= diff12 and diff23 <= diff13:
            nota_consenso = (s2 + s3) / 2
        else:
            nota_consenso = (s1 + s2) / 2

        correcao_final['competencias'].append({
            "competencia": i + 1,
            "nota": nota_consenso,
            "justificativa": f"[Consenso C{i+1}] Notas da banca: ({s1}, {s2}, {s3}). Nota final da competência: {nota_consenso}."
        })

    correcao_final['nota_final'] = sum(c['nota'] for c in correcao_final['competencias'])
    return correcao_final

async def simular_banca_corretora_async(texto_redacao: str, tema: str) -> Dict[str, Any]:
    print("--- INICIANDO BANCA CORRETORA (ARQUITETURA MULTIAGENTE) ---")
    correcao_1, correcao_2 = await asyncio.gather(
        executar_correcao_completa_async("Corretor 1", texto_redacao, tema),
        executar_correcao_completa_async("Corretor 2", texto_redacao, tema)
    )
    
    if verificar_discrepancia(correcao_1, correcao_2):
        correcao_supervisor = await executar_correcao_completa_async("Corretor Supervisor", texto_redacao, tema)
        return resolver_discrepancia_com_supervisor(correcao_1, correcao_2, correcao_supervisor)
    else:
        return calcular_nota_consolidada(correcao_1, correcao_2)

# --- Tarefa Principal do Celery ---
@celery_app.task(name="correct_essay")
def correct_essay(redacao_id: int):
    """
    Ponto de entrada para a tarefa de correção em background.
    """
    db: Session = SessionLocal()
    try:
        redacao = db.query(Redacao).filter(Redacao.id == redacao_id).first()
        if not redacao:
            print(f"Erro: Redação com ID {redacao_id} não encontrada.")
            return

        print(f"Iniciando correção da redação ID: {redacao_id}")
        redacao.status = "PROCESSANDO"
        db.commit()

        # Executa a simulação completa da banca corretora
        resultado_final = asyncio.run(simular_banca_corretora_async(redacao.texto_redacao, redacao.tema))
        
        redacao.resultado_json = resultado_final
        redacao.status = "CONCLUIDO"
        db.commit()
        print(f"Correção da redação ID: {redacao_id} finalizada com sucesso.")
    except Exception as e:
        db.rollback()
        redacao_a_atualizar = db.query(Redacao).filter(Redacao.id == redacao_id).first()
        if redacao_a_atualizar:
            redacao_a_atualizar.status = "ERRO"
            redacao_a_atualizar.resultado_json = {"erro": str(e)}
            db.commit()
        print(f"Erro ao corrigir redação ID {redacao_id}: {e}")
    finally:
        db.close()