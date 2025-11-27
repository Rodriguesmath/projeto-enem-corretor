from typing import Dict, Any


def verificar_discrepancia(c1: Dict[str, Any], c2: Dict[str, Any]) -> bool:
    """Verifica se há discrepância total ou por competência."""
    if abs(c1["nota_final"] - c2["nota_final"]) > 100:
        print(f"Discrepância TOTAL detectada: {c1['nota_final']} vs {c2['nota_final']}")
        return True
    for comp1, comp2 in zip(c1["competencias"], c2["competencias"]):
        if abs(comp1["nota"] - comp2["nota"]) > 80:
            print(
                f"Discrepância na Competência {comp1['competencia']} detectada: {comp1['nota']} vs {comp2['nota']}"
            )
            return True
    return False


def calcular_nota_consolidada(c1: Dict[str, Any], c2: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula a média simples entre dois corretores."""
    print("--- SEM DISCREPÂNCIA. Calculando média por competência. ---")

    correcao_final = {
        "competencias": [],
        "nota_final": 0,
        "fonte_resultado": "Média dos Corretores 1 e 2",
        "detalhes": [c1, c2],
    }

    for comp1, comp2 in zip(c1["competencias"], c2["competencias"]):
        nota_media_comp = (comp1["nota"] + comp2["nota"]) / 2

        correcao_final["competencias"].append(
            {
                "competencia": comp1["competencia"],
                "nota": nota_media_comp,
                "justificativa": f"[Média C{comp1['competencia']}] Corretor 1 ({comp1['nota']}): {comp1['justificativa']} | Corretor 2 ({comp2['nota']}): {comp2['justificativa']}",
            }
        )

    correcao_final["nota_final"] = sum(
        c["nota"] for c in correcao_final["competencias"]
    )
    return correcao_final


def resolver_discrepancia_com_supervisor(
    c1: Dict[str, Any], c2: Dict[str, Any], c3: Dict[str, Any]
) -> Dict[str, Any]:
    """Calcula o consenso da banca pegando a média das 2 notas mais próximas."""
    print(
        "--- DISCREPÂNCIA DETECTADA! Resolvendo com base nas duas notas mais próximas por competência. ---"
    )

    correcao_final = {
        "competencias": [],
        "nota_final": 0,
        "fonte_resultado": "Consenso da Banca (média das 2 notas mais próximas)",
        "detalhes": [c1, c2, c3],
    }

    for i in range(5):
        s1 = c1["competencias"][i]["nota"]
        s2 = c2["competencias"][i]["nota"]
        s3 = c3["competencias"][i]["nota"]

        diff13 = abs(s1 - s3)
        diff23 = abs(s2 - s3)
        diff12 = abs(s1 - s2)

        nota_consenso = 0

        if diff13 <= diff12 and diff13 <= diff23:
            nota_consenso = (s1 + s3) / 2
        elif diff23 <= diff12 and diff23 <= diff13:
            nota_consenso = (s2 + s3) / 2
        else:
            nota_consenso = (s1 + s2) / 2

        correcao_final["competencias"].append(
            {
                "competencia": i + 1,
                "nota": nota_consenso,
                "justificativa": f"[Consenso C{i+1}] Notas da banca: ({s1}, {s2}, {s3}). Nota final da competência: {nota_consenso}.",
            }
        )

    correcao_final["nota_final"] = sum(
        c["nota"] for c in correcao_final["competencias"]
    )
    return correcao_final
