# Importações Padrão
import os
import json
import asyncio
import re # Para Expressões Regulares (extrair tempo do erro)
import math # Para arredondar o tempo
import time # Para pausas síncronas
from celery import Celery
from sqlalchemy.orm import Session
from shared.models import SessionLocal, Redacao
from dotenv import load_dotenv

# Importações do LangChain e Google
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any

# Importação específica para o erro de Rate Limit
from google.api_core.exceptions import ResourceExhausted

# Carrega variáveis de ambiente (ex: GOOGLE_API_KEY) do arquivo .env
load_dotenv()

# Configuração do Celery App
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

# --- PROTEÇÃO NÍVEL 1 (CELERY) ---
# Garante que o Celery só puxe 1 tarefa por minuto
# Isso evita que 2 tarefas executem ao mesmo tempo e estourem o limite
celery_app.conf.update(
    task_routes={'tasks.correct_essay': {'queue': 'correcoes'}},
    task_rate_limit='1/m' # Limita a 1 tarefa por minuto
)

# --- Modelos Pydantic para a Estrutura de Saída ---
class AvaliacaoCompetencia(BaseModel):
    competencia: int = Field(description="O número da competência (de 1 a 5)")
    nota: int = Field(description="A nota para esta competência (0, 40, 80, 120, 160, ou 200)")
    justificativa: str = Field(description="A explicação detalhada para a nota atribuída.")

class CorrecaoCompleta(BaseModel):
    competencias: List[AvaliacaoCompetencia]
    nota_final: int = Field(description="A soma das notas das cinco competências.")
    comentarios_gerais: str = Field(description="Um parágrafo com comentários gerais e sugestões.")
    id_corretor: str = Field(description="A ID do corretor (ex: 'Corretor 1')")


# --- Lógica Multiagente (5 Agentes por Corretor) ---

PROMPT_AGENTE_COMPETENCIA = ChatPromptTemplate.from_template(
    """Você é um corretor especialista do ENEM focado EXCLUSIVAMENTE na Competência {competencia_numero}.

    lembre-se, a nota vai de 0 a 200

    Sua única tarefa é analisar a redação a seguir e atribuir uma nota e justificativa apenas para a Competência {competencia_numero}.

    Critérios de Avaliação para a Competência {competencia_numero}:
    {criterios_competencia}

    Redação para Análise:
    ---
    {redacao}
    ---
    
    Nuances:

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
    
    # Força o Gemini a retornar JSON
    llm_com_json = llm.with_structured_output(AvaliacaoCompetencia)
    
    chain = PROMPT_AGENTE_COMPETENCIA | llm_com_json
    
    resultado = await chain.ainvoke({
        "competencia_numero": comp_info['numero'],
        "criterios_competencia": comp_info['criterios'],
        "redacao": texto_redacao,
        "tema": tema,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Converte o objeto Pydantic em um dict para serialização JSON
    return resultado.dict()

async def executar_correcao_completa_async(id_corretor: str, texto_redacao: str, tema: str) -> Dict[str, Any]:
    """
    Esta função é o "Agente Corretor Orquestrador".
    Ele gerencia 5 sub-agentes (um para cada competência) em paralelo.
    """
    print(f"[{id_corretor}] Orquestrando 5 agentes de competência em paralelo...")
    
    temperatura = 0.4 if id_corretor == "Corretor 1" else 0.6
    
    # Usando o modelo que você preferiu e que está na sua lista
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest", 
        temperature=temperatura
    )

    competencias_info = [
        {
            'numero': 1,
            'criterios': """
            Avalie o domínio da modalidade escrita formal da Língua Portuguesa.
            - 200 pontos: Domínio excelente. Estrutura sintática complexa e sem desvios.
            - 160 pontos: Bom domínio. Estrutura sintática boa e poucos desvios.
            - 120 pontos: Domínio mediano. Estrutura sintática simples e com alguns desvios.
            - 80 pontos: Domínio insuficiente. Muitos desvios e estrutura sintática deficiente.
            - 40 pontos: Domínio precário. Numerosos desvios e estrutura sintática inadequada.
            - 0 pontos: Desconhecimento da modalidade escrita formal.
            """
        },
        {
            'numero': 2,
            'criterios': """
            Avalie a compreensão do tema e o uso de repertório sociocultural.
            - 200 pontos: Aborda o tema completamente, com repertório legitimado, pertinente e de uso produtivo, e excelente domínio do texto dissertativo-argumentativo.
            - 160 pontos: Aborda o tema completamente, com repertório legitimado e pertinente, e bom domínio do texto dissertativo-argumentativo.
            - 120 pontos: Aborda o tema completamente, com repertório previsível, e mediano domínio do texto.
            - 80 pontos: Aborda o tema de forma tangencial, com repertório pouco pertinente ou baseado no senso comum.
            - 40 pontos: Fuga ao tema ou repertório desconectado.
            - 0 pontos: Fuga total ao tema.
            """
        },
        {
            'numero': 3,
            'criterios': """
            Avalie a organização das ideias e a defesa de um ponto de vista.
            - 200 pontos: Apresenta informações com projeto de texto estratégico, desenvolvimento consistente e sem contradições. Argumentação excelente.
            - 160 pontos: Apresenta informações com projeto de texto, com desenvolvimento consistente. Argumentação boa.
            - 120 pontos: Apresenta informações com projeto de texto, mas com desenvolvimento limitado ou algumas contradições. Argumentação mediana.
            - 80 pontos: Apresenta informações desorganizadas, contraditórias ou pouco relacionadas ao tema. Argumentação fraca.
            - 40 pontos: Apresenta informações desconexas.
            - 0 pontos: Não atende ao tipo textual.
            """
        },
        {
            'numero': 4,
            'criterios': """
            Avalie o uso dos mecanismos de coesão textual.
            - 200 pontos: Articula bem as partes do texto, com repertório coesivo diversificado e sem inadequações.
            - 160 pontos: Articula bem as partes do texto, com repertório coesivo e poucas inadequações.
            - 120 pontos: Articula as partes do texto de forma mediana, com repertório coesivo pouco diversificado e algumas inadequações.
            - 80 pontos: Articula as partes do texto de forma insuficiente, com repertório coesivo limitado e muitas inadequações.
            - 40 pontos: Articula as partes do texto de forma precária.
            - 0 pontos: Ausência de articulação.
            """
        },
        {
            'numero': 5,
            'criterios': """
            Avalie a elaboração da proposta de intervenção.
            - 200 pontos: Propõe intervenção excelente, completa (5 elementos: ação, agente, modo/meio, efeito, detalhamento), articulada à discussão e detalhada.
            - 160 pontos: Propõe intervenção boa, com os 5 elementos, mas com detalhamento limitado ou articulação mediana.
            - 120 pontos: Propõe intervenção suficiente, com 4 dos 5 elementos.
            - 80 pontos: Propõe intervenção insuficiente, com 3 dos 5 elementos.
            - 40 pontos: Propõe intervenção precária, com 1 ou 2 elementos, ou que desrespeita os direitos humanos.
            - 0 pontos: Ausência de proposta de intervenção.
            """
        }
    ]

    # --- PROTEÇÃO NÍVEL 2 (ASYNCIO) ---
    # Executa as 5 chamadas de competência em paralelo (Pico de 5 chamadas)
    tasks = [avaliar_competencia_async(llm, texto_redacao, tema, info) for info in competencias_info]
    resultados_competencias = await asyncio.gather(*tasks)
    
    resultados_competencias.sort(key=lambda x: x['competencia'])

    nota_final_calculada = sum(r['nota'] for r in resultados_competencias)
    
    # --- Pico de +1 chamada --- (Total de 6 chamadas em paralelo para este corretor)
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


# --- Tarefa Principal do Celery (com Estado) ---
@celery_app.task(name="correct_essay", bind=True)
def correct_essay(self, redacao_id: int, correcao_1_json: str = None, correcao_2_json: str = None, correcao_supervisor_json: str = None):
    """
    Ponto de entrada para a tarefa de correção em background.
    Agora é uma tarefa "com estado" para suportar retries.
    """
    db: Session = SessionLocal()
    redacao = None # Definido para garantir o 'finally'
    
    # Resultados parciais
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

        # --- Etapa 1: Corretor 1 ---
        if not c1:
            print("Executando Corretor 1...")
            c1 = asyncio.run(executar_correcao_completa_async("Corretor 1", redacao.texto_redacao, redacao.tema))
            print("Corretor 1 finalizado. Pausando para não estourar o limite...")
            # Pausa síncrona para "respirar" a cota da API
            time.sleep(15) 
        else:
            print("Pulando Corretor 1 (resultado já existe do retry).")

        # --- Etapa 2: Corretor 2 ---
        if not c2:
            print("Executando Corretor 2...")
            c2 = asyncio.run(executar_correcao_completa_async("Corretor 2", redacao.texto_redacao, redacao.tema))
            print("Corretor 2 finalizado.")
        else:
            print("Pulando Corretor 2 (resultado já existe do retry).")
            
        # --- Etapa 3: Verificar Discrepância ---
        if not verificar_discrepancia(c1, c2):
            # SEM DISCREPÂNCIA
            resultado_final = calcular_nota_consolidada(c1, c2)
        else:
            # COM DISCREPÂNCIA, precisa do supervisor
            if not c3:
                print("Discrepância detectada. Pausando e executando Corretor Supervisor...")
                time.sleep(15) # Mais uma pausa antes do 3º corretor
                c3 = asyncio.run(executar_correcao_completa_async("Corretor Supervisor", redacao.texto_redacao, redacao.tema))
                print("Corretor Supervisor finalizado.")
            else:
                 print("Pulando Corretor Supervisor (resultado já existe do retry).")
            
            resultado_final = resolver_discrepancia_com_supervisor(c1, c2, c3)

        
        redacao.resultado_json = resultado_final
        redacao.status = "CONCLUIDO"
        db.commit()
        print(f"Correção da redação ID: {redacao_id} finalizada com sucesso.")

    except ResourceExhausted as e:
        # --- PROTEÇÃO NÍVEL 3 (RETRY INTELIGENTE) ---
        db.rollback()
        print(f"Erro de Limite de Taxa (429) detectado: {e}")

        # Tenta extrair o tempo de espera sugerido pela API
        countdown_seconds = 60  # Padrão
        try:
            # Procura por padrões como "Please retry in 20.021s"
            match = re.search(r'Please retry in (\d+\.?\d*)', str(e))
            if match:
                # Pega o tempo, arredonda para cima, e soma 1s de margem
                wait_time = float(match.group(1))
                countdown_seconds = math.ceil(wait_time) + 1
                print(f"API sugeriu esperar {wait_time}s. Reagendando em {countdown_seconds}s.")
            else:
                print(f"Não foi possível extrair o tempo de espera. Usando padrão de {countdown_seconds}s.")
        except Exception as re_e:
            print(f"Erro ao extrair tempo de espera: {re_e}. Usando padrão de 60s.")

        # Passa os resultados parciais para a próxima tentativa
        raise self.retry(
            exc=e, 
            countdown=countdown_seconds, 
            max_retries=5,
            kwargs={
                'redacao_id': redacao_id,
                'correcao_1_json': json.dumps(c1) if c1 else None,
                'correcao_2_json': json.dumps(c2) if c2 else None,
                'correcao_supervisor_json': json.dumps(c3) if c3 else None,
            }
        )
        
    except Exception as e:
        db.rollback()
        if redacao: # Só atualiza se a redação foi carregada
            redacao.status = "ERRO"
            redacao.resultado_json = {"erro": str(e)}
            db.commit()
        print(f"Erro GERAL ao corrigir redação ID {redacao_id}: {e}")
    finally:
        db.close()

