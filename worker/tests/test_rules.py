from worker.banca.rules import verificar_discrepancia, calcular_nota_consolidada, resolver_discrepancia_com_supervisor

def criar_correcao_mock(nota_total, competencias=[120, 120, 120, 120, 120]):
    return {
        "nota_final": nota_total,
        "competencias": [{"nota": n} for n in competencias]
    }

def test_verificar_discrepancia_nota_total():
    # Diferença > 100
    c1 = criar_correcao_mock(800)
    c2 = criar_correcao_mock(600)
    assert verificar_discrepancia(c1, c2) is True

    # Diferença <= 100
    c1 = criar_correcao_mock(800)
    c2 = criar_correcao_mock(700)
    assert verificar_discrepancia(c1, c2) is False

def test_verificar_discrepancia_competencia():
    # Diferença > 80 em uma competência
    c1 = criar_correcao_mock(600, [120, 120, 120, 120, 120])
    c2 = criar_correcao_mock(600, [120, 120, 120, 120, 40])
    
    c1 = criar_correcao_mock(600, [200, 120, 120, 120, 120])
    c2 = criar_correcao_mock(600, [80, 120, 120, 120, 120]) # Diff 120
    assert verificar_discrepancia(c1, c2) is True
    
    c1 = criar_correcao_mock(600, [120, 120, 120, 120, 120])
    c2 = criar_correcao_mock(600, [120, 120, 120, 120, 120]) # Iguais
    assert verificar_discrepancia(c1, c2) is False

def test_calcular_nota_consolidada():
    c1 = criar_correcao_mock(800)
    c2 = criar_correcao_mock(700)
    final = calcular_nota_consolidada(c1, c2)
    # Média: 750
    assert final["nota_final"] == 750
