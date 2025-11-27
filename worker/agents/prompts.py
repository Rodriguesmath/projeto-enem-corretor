from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate

# 1. Prompt com Persona Rigorosa e Ordem de Pensamento
PROMPT_AGENTE_COMPETENCIA = ChatPromptTemplate.from_template(
    """Você é um corretor SÊNIOR da BANCA OFICIAL DO ENEM (INEP), conhecido por ser EXTREMAMENTE RIGOROSO, técnico e imparcial.
Sua função NÃO é elogiar o aluno, mas sim auditar o texto em busca de falhas, lacunas e desvios conforme a Grade Oficial.

Você está avaliando EXCLUSIVAMENTE a Competência {competencia_numero}.

=== O QUE VOCÊ DEVE PROCURAR (ANTI-CRITÉRIOS) ===
Para não inflar a nota, verifique ativamente:
{criterios_negativos}

=== CRITÉRIOS DE PONTUAÇÃO (Competência {competencia_numero}) ===
{criterios_competencia}

=== REDAÇÃO DO ALUNO ===
{redacao}
=======================

Tema: {tema}

=== INSTRUÇÕES DE RACIOCÍNIO ===
1. Primeiro, procure evidências de falhas descritas nos "Anti-Critérios".
2. Se encontrar falhas graves, a nota cai para o nível correspondente imediatamente.
3. Texto "bonito" ou "bem formatado" NÃO garante nota 200. O conteúdo precisa ser profundo.

=== INSTRUÇÕES DE SAÍDA ===
Retorne sua análise estritamente no formato JSON.
O JSON deve conter um campo "analise_critica" (string) onde você aponta os erros ANTES de dar a "nota" (int).
{format_instructions}
"""
)

# 2. Critérios Refinados com "Anti-Critérios" (O Segredo da Rigidez)
COMPETENCIAS_INFO: List[Dict[str, Any]] = [
    {
        "numero": 1,
        "criterios_negativos": """
        - NÃO ignore erros de vírgula ou crase só porque o texto parece culto.
        - Estruturas sintáticas complexas não salvam erros básicos.
        - Procure ativamente por: truncamento de períodos, justaposição de orações e falhas de concordância verbal/nominal.
        - Se houver 2 ou mais desvios gramaticais distintos, a nota MÁXIMA é 160.
        """,
        "criterios": """
        - 200 pontos: Domínio excelente. Estrutura sintática complexa (máximo 1 falha) e sem desvios gramaticais (máximo 2 leves).
        - 160 pontos: Bom domínio. Estrutura sintática boa e poucos desvios que não prejudicam a fluidez.
        - 120 pontos: Domínio mediano. Estrutura sintática simples e com alguns desvios frequentes.
        - 80 pontos: Domínio insuficiente. Muitos desvios gramaticais e estrutura sintática deficiente.
        - 40 pontos: Domínio precário. Numerosos desvios e estrutura sintática inadequada (oralidade).
        - 0 pontos: Desconhecimento da modalidade escrita formal.
        """.strip(),
    },
    {
        "numero": 2,
        "criterios_negativos": """
        - Citações "Coringa" (que servem para qualquer tema, ex: "Segundo a Constituição...", "Utopia de More") DEVEM ser penalizadas se não estiverem especificamente ligadas à discussão do tema concreto.
        - Se o aluno cita um autor mas não usa a ideia dele para argumentar (uso legitimado mas improdutivo), a nota MÁXIMA é 120 ou 160.
        - Verifique se o texto não está apenas tangenciando o tema.
        """,
        "criterios": """
        - 200 pontos: Aborda o tema completamente, com repertório legitimado, pertinente e de USO PRODUTIVO (a citação fundamenta a discussão).
        - 160 pontos: Aborda o tema completamente, com repertório legitimado e pertinente, mas SEM uso produtivo (citação "enfeite").
        - 120 pontos: Aborda o tema completamente, mas com repertório previsível ou baseado no senso comum.
        - 80 pontos: Aborda o tema de forma tangencial, com repertório pouco pertinente.
        - 40 pontos: Fuga ao tema ou repertório desconectado.
        - 0 pontos: Fuga total ao tema.
        """.strip(),
    },
    {
        "numero": 3,
        "criterios_negativos": """
        - ESTA É A COMPETÊNCIA MAIS DIFÍCIL. SEJA SEVERO.
        - Penalize "Listas de Fatos": o aluno apenas joga informações sem explicar o "porquê" ou as consequências sociais profundas.
        - Penalize "Senso Comum": argumentos óbvios (ex: "precisa melhorar a educação") sem detalhamento crítico.
        - Procure por "Lacunas Argumentativas": afirmações fortes sem explicação lógica subsequente.
        - Se o texto é apenas organizado, mas superficial, a nota é 120 ou 160. NUNCA 200.
        """,
        "criterios": """
        - 200 pontos: Autoria forte. O aluno sai do senso comum, critica as causas estruturais do problema. Projeto de texto estratégico visível e desenvolvimento consistente.
        - 160 pontos: Texto organizado, com começo, meio e fim, mas argumentos previsíveis ou pouco aprofundados.
        - 120 pontos: Projeto de texto com falhas. Argumentação limitada, redundante ou com lacunas claras.
        - 80 pontos: Apresenta informações desorganizadas, contraditórias ou pouco relacionadas ao tema.
        - 40 pontos: Apresenta informações desconexas (monobloco).
        - 0 pontos: Não atende ao tipo textual dissertativo-argumentativo.
        """.strip(),
    },
    {
        "numero": 4,
        "criterios_negativos": """
        - Repetição de palavras (ex: usar "internet" 5 vezes) deve baixar a nota.
        - Uso de conectivos "esqueleto" (ex: "Em primeira análise") garante nota base, mas não nota máxima se não houver variedade interna nos parágrafos.
        - Verifique conectivos equivocados (usar "Contudo" para adicionar ideia, em vez de opor).
        """,
        "criterios": """
        - 200 pontos: Articula bem as partes do texto, com repertório coesivo diversificado (intra e interparágrafos) e sem inadequações.
        - 160 pontos: Articula bem as partes do texto, com repertório coesivo e poucas inadequações ou repetições.
        - 120 pontos: Articula as partes do texto de forma mediana, com repertório coesivo pouco diversificado e algumas inadequações.
        - 80 pontos: Articula as partes do texto de forma insuficiente, com repertório coesivo limitado e muitas inadequações.
        - 40 pontos: Articula as partes do texto de forma precária.
        - 0 pontos: Ausência de articulação.
        """.strip(),
    },
    {
        "numero": 5,
        "criterios_negativos": """
        - NÃO dê 200 pontos apenas porque existem 5 elementos.
        - O DETALHAMENTO deve ser uma informação EXTRA válida, não apenas uma repetição ("o governo deve fazer X, pois o governo pode").
        - Ação nula (ex: "conscientizar a população") é considerada fraca se não vier acompanhada de mecanismos práticos.
        """,
        "criterios": """
        - 200 pontos: Propõe intervenção excelente, completa (5 elementos: Ação, Agente, Modo/Meio, Efeito, Detalhamento), muito bem articulada à discussão.
        - 160 pontos: Propõe intervenção boa, com os 5 elementos, mas o detalhamento é fraco ou a articulação com o texto é mediana.
        - 120 pontos: Propõe intervenção suficiente, com 4 dos 5 elementos válidos.
        - 80 pontos: Propõe intervenção insuficiente, com 3 dos 5 elementos.
        - 40 pontos: Propõe intervenção precária, com 1 ou 2 elementos, ou que desrespeita os direitos humanos (anula a competência se desrespeitar).
        - 0 pontos: Ausência de proposta de intervenção.
        """.strip(),
    },
]