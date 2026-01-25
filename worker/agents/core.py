import asyncio
import json
import logging
import os
from google.api_core.exceptions import ResourceExhausted
from typing import Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .prompts import PROMPT_AGENTE_COMPETENCIA, COMPETENCIAS_INFO
from shared.schemas import AvaliacaoCompetencia
from shared.config import settings

logger = logging.getLogger(__name__)

# Configuração Google Gemini / Perplexity
# Pega do ambiente ou usa o Flash Latest como fallback
LLM_PROVIDER = settings.LLM_PROVIDER.lower()
MODEL_NAME = settings.LLM_MODEL

# Temperaturas otimizadas para precisão uniforme em todas as faixas de nota
TEMP_CORRETOR_PADRAO = 0.25  # Corretor 2 (rigoroso)
TEMP_CORRETOR_RIGOROSO = 0.20  # Corretor 1 (muito rigoroso)

# Personas calibradas: Justos e discernentes (alinhados com critérios oficiais ENEM)
PERSONAS = {
    "Corretor 1": "Seu perfil é TÉCNICO e CRITERIOSO. Você valoriza a correção gramatical e reconhece textos excelentes, mas é capaz de identificar pequenas falhas que impedem a nota máxima. Você segue os critérios oficiais do ENEM com fidelidade.",
    "Corretor 2": "Seu perfil é CONTEXTUAL e EQUILIBRADO. Você valoriza profundidade argumentativa e coesão, mas diferencia textos excelentes (180-200) de textos perfeitos (200). Você é justo e reconhece qualidade sem ser permissivo.",
    "Corretor Supervisor": "Seu perfil é EQUILIBRADO e FIEL aos critérios oficiais do ENEM. Você busca precisão, diferenciando textos muito bons (840-920) de textos perfeitos (960-1000).",
}

async def avaliar_competencia_individual(
    llm: BaseChatModel, 
    texto_redacao: str, 
    tema: str, 
    comp_info: Dict[str, Any],
    instrucoes_persona: str
) -> Dict[str, Any]:
    """
    Avalia uma competência.
    """
    # Loop infinito de "Semáforo" para Rate Limit
    while True:
        try:
            parser = JsonOutputParser(pydantic_object=AvaliacaoCompetencia)
            
            chain = PROMPT_AGENTE_COMPETENCIA | llm | parser

            # Aumentei o timeout aqui também por segurança
            resultado = await chain.ainvoke({
                "instrucoes_persona": instrucoes_persona,
                "competencia_numero": comp_info["numero"],
                "criterios_competencia": comp_info["criterios"],
                "criterios_negativos": comp_info.get("criterios_negativos", ""), 
                "redacao": texto_redacao,
                "tema": tema,
                "format_instructions": parser.get_format_instructions(),
            })

            return resultado

        except ResourceExhausted as e:
            # Semáforo Vermelho 🔴
            wait_time = 30.0 # Default
            # Tenta pegar tempo sugerido pelo Google
            if hasattr(e, 'retry_after'):
                wait_time = float(e.retry_after)
            
            logger.warning(f"Rate Limit (429) no Gemini. Pausando por {wait_time}s antes de tentar de novo...")
            await asyncio.sleep(wait_time)
            continue # Tenta de novo (Semáforo Verde 🟢)

        except Exception as e:
            logger.error(f"Erro ao avaliar competência {comp_info.get('numero')}: {e}")
            return {
                "competencia": comp_info.get("numero"),
                "nota": 0,
                "justificativa": f"Erro sistêmico: {str(e)}"
            }


async def _gerar_feedback_geral(
    llm: BaseChatModel, 
    avaliacoes: List[Dict[str, Any]]
) -> str:
    while True:
        try:
            prompt_comentario = ChatPromptTemplate.from_template(
                "Com base nestas avaliações, escreva um feedback geral curto e motivador para o aluno. "
                "Texto corrido apenas. Avaliações: {avaliacoes}"
            )
            chain = prompt_comentario | llm
            resultado = await chain.ainvoke({"avaliacoes": json.dumps(avaliacoes, ensure_ascii=False)})
            return resultado.content
            
        except ResourceExhausted as e:
            # Semáforo Vermelho 🔴
            wait_time = 30.0
            logger.warning(f"Rate Limit no Feedback. Pausando por {wait_time}s...")
            await asyncio.sleep(wait_time)
            continue

        except Exception as e:
            logger.error(f"Erro ao gerar feedback geral: {e}")
            return "Erro ao gerar comentário final."


def get_llm_client(temperature: float = 0.2, json_mode: bool = True) -> BaseChatModel:
    """
    Fábrica de LLMs: Retorna Gemini ou Perplexity conforme configuração.
    """
    if LLM_PROVIDER == "perplexity":
        pplx_key = settings.PPLX_API_KEY
        if not pplx_key:
            logger.error("PERPLEXITY_API_KEY não configurada!")
        
        return ChatOpenAI(
            model=MODEL_NAME, 
            temperature=temperature,
            openai_api_key=pplx_key,
            base_url="https://api.perplexity.ai",
            max_tokens=2048,
            timeout=60.0,
        )
    
    # Default: Gemini
    api_key = settings.GOOGLE_API_KEY
    kwargs = {}
    if json_mode:
        kwargs["response_mime_type"] = "application/json"

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=temperature,
        google_api_key=api_key,
        max_output_tokens=2048,
        timeout=60.0,
        model_kwargs=kwargs
    )


async def executar_correcao_completa_async(
    id_corretor: str, 
    texto_redacao: str, 
    tema: str
) -> Dict[str, Any]:
    """
    Orquestrador SEQUENCIAL (Modelo Gemini).
    """
    persona_instrucao = PERSONAS.get(id_corretor, PERSONAS["Corretor Supervisor"])
    logger.info(f"[{id_corretor}] Iniciando correção COM {LLM_PROVIDER.upper()} e persona: {persona_instrucao[:30]}...")

    temperatura = TEMP_CORRETOR_RIGOROSO if id_corretor == "Corretor 1" else TEMP_CORRETOR_PADRAO
    
    llm = get_llm_client(temperature=temperatura, json_mode=True)

    resultados_competencias = []

    # --- LOOP SEQUENCIAL ---
    for info in COMPETENCIAS_INFO:
        logger.info(f"[{id_corretor}] Processando Competência {info['numero']}...")
        res = await avaliar_competencia_individual(llm, texto_redacao, tema, info, persona_instrucao)
        resultados_competencias.append(res)

    # Ordenação
    resultados_competencias.sort(key=lambda x: x.get("competencia", 0))

    # Cálculo
    nota_final_calculada = 0
    competencias_validas = 0
    for r in resultados_competencias:
        if isinstance(r, dict) and isinstance(r.get("nota"), (int, float)):
            nota_final_calculada += r["nota"]
            if r.get("nota", 0) > 0:
                competencias_validas += 1

    # Feedback (Se tudo deu certo)
    else:
        logger.info(f"[{id_corretor}] Gerando feedback final...")
        # Instância sem JSON forçado para o texto livre
        llm_texto = get_llm_client(temperature=0.7, json_mode=False)
        comentario_geral = await _gerar_feedback_geral(llm_texto, resultados_competencias)

    logger.info(f"[{id_corretor}] FIM. Nota: {nota_final_calculada}")

    return {
        "competencias": resultados_competencias,
        "nota_final": nota_final_calculada,
        "comentarios_gerais": comentario_geral,
        "id_corretor": id_corretor,
    }