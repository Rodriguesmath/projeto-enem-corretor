import asyncio
import json
import logging
from typing import Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Imports internos
from .prompts import PROMPT_AGENTE_COMPETENCIA, COMPETENCIAS_INFO
from shared.schemas import AvaliacaoCompetencia

# Configuração de Logs
logger = logging.getLogger(__name__)

# Constantes de Configuração
MODEL_NAME = "models/gemini-flash-latest"
TEMP_CORRETOR_PADRAO = 0.2
TEMP_CORRETOR_RIGOROSO = 0.1


async def avaliar_competencia_individual(
    llm: ChatGoogleGenerativeAI, 
    texto_redacao: str, 
    tema: str, 
    comp_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Agente Especialista: Avalia uma única competência do ENEM de forma isolada.
    
    Args:
        llm: Instância do modelo de linguagem configurada.
        texto_redacao: O texto da redação a ser corrigida.
        tema: O tema da redação.
        comp_info: Dicionário contendo metadados da competência (número, critérios).

    Returns:
        Dict: Dicionário contendo a nota e a justificativa da competência.
    """
    try:
        # Configura o parser para garantir que a saída obedeça ao schema Pydantic
        parser = JsonOutputParser(pydantic_object=AvaliacaoCompetencia)
        
        # O uso de with_structured_output força o modelo a retornar JSON estrito
        llm_estruturado = llm.with_structured_output(AvaliacaoCompetencia)

        chain = PROMPT_AGENTE_COMPETENCIA | llm_estruturado

        resultado = await chain.ainvoke({
            "competencia_numero": comp_info["numero"],
            "criterios_competencia": comp_info["criterios"],
            "criterios_negativos": comp_info.get("criterios_negativos", ""), 
            "redacao": texto_redacao,
            "tema": tema,
            "format_instructions": parser.get_format_instructions(),
        })

        return resultado.dict()

    except Exception as e:
        logger.error(f"Erro ao avaliar competência {comp_info.get('numero')}: {e}")
        # Em caso de erro, retorna uma estrutura zerada para não quebrar o fluxo
        return {
            "competencia": comp_info.get("numero"),
            "nota": 0,
            "justificativa": f"Erro sistêmico ao avaliar esta competência: {str(e)}"
        }


async def _gerar_feedback_geral(
    llm: ChatGoogleGenerativeAI, 
    avaliacoes: List[Dict[str, Any]]
) -> str:
    """
    Função auxiliar para gerar um parágrafo de feedback consolidado.
    """
    try:
        prompt_comentario = ChatPromptTemplate.from_template(
            "Com base nestas 5 avaliações de competências de uma redação, "
            "escreva um parágrafo de comentário geral conciso, motivador e útil para o aluno. "
            "Avaliações: {avaliacoes}"
        )
        chain = prompt_comentario | llm
        
        # Serializa as avaliações para passar como contexto
        resultado = await chain.ainvoke({"avaliacoes": json.dumps(avaliacoes, ensure_ascii=False)})
        return resultado.content
    except Exception as e:
        logger.error(f"Erro ao gerar feedback geral: {e}")
        return "Não foi possível gerar o comentário geral devido a um erro no processamento."


async def executar_correcao_completa_async(
    id_corretor: str, 
    texto_redacao: str, 
    tema: str
) -> Dict[str, Any]:
    """
    Agente Orquestrador: Gerencia a correção completa da redação.
    
    Responsabilidades:
    1. Instanciar o modelo com a temperatura adequada.
    2. Paralelizar a avaliação das 5 competências.
    3. Consolidar as notas e gerar feedback final.
    """
    logger.info(f"[{id_corretor}] Iniciando orquestração de correção...")

    # Definição de temperatura baseada no perfil do corretor
    # 'Corretor 1' tende a ser mais rigoroso/conservador (temperatura menor)
    temperatura = TEMP_CORRETOR_RIGOROSO if id_corretor == "Corretor 1" else TEMP_CORRETOR_PADRAO

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME, 
        temperature=temperatura
    )

    # Criação das tarefas assíncronas (uma para cada competência)
    tasks = [
        avaliar_competencia_individual(llm, texto_redacao, tema, info)
        for info in COMPETENCIAS_INFO
    ]

    # Execução paralela (Scatter-Gather)
    resultados_competencias = await asyncio.gather(*tasks)

    # Ordenação por número da competência para garantir consistência visual (C1 a C5)
    resultados_competencias.sort(key=lambda x: x["competencia"])

    # Cálculo da nota final
    nota_final_calculada = sum(r["nota"] for r in resultados_competencias if isinstance(r.get("nota"), (int, float)))

    # Geração do comentário geral (aproveita a instância do LLM já criada)
    comentario_geral = await _gerar_feedback_geral(llm, resultados_competencias)

    logger.info(f"[{id_corretor}] Correção finalizada. Nota: {nota_final_calculada}")

    # Retorno estruturado
    return {
        "competencias": resultados_competencias,
        "nota_final": nota_final_calculada,
        "comentarios_gerais": comentario_geral,
        "id_corretor": id_corretor,
    }