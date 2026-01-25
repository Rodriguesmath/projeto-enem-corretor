#!/usr/bin/env python3
"""
Teste Completo de Precisão - Corretor ENEM IA
Envia 6 redações (todas as faixas de nota) e coleta resultados.
"""

import requests
import json
import time

# Token JWT gerado anteriormente (assumindo que ainda é válido, senão gerar novo)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZV9maW5hbEBleGVtcGxvLmNvbSIsImV4cCI6MTc2OTMxMDQ4Nn0.wC5Hfx_UR5VoOBqB_F-pVQ9eZSaWXzfdxGKAZHd9vG8"
BASE_URL = "http://localhost:8000/api/v1/redacoes/"

REDACOES = [
    {
        "nota_oficial": 980,
        "nome": "980 - Kant/IBGE/Durkheim",
        "tema": "A persistência da invisibilidade do trabalho de cuidado realizado pela mulher no Brasil",
        "texto": "O filósofo iluminista Immanuel Kant afirma que o homem é o que a educação faz dele. Nesse contexto, a estrutura educacional e social brasileira, historicamente patriarcal, moldou a percepção de que o trabalho doméstico e de cuidado é uma obrigação intrínseca ao gênero feminino. No entanto, essa construção cultural gera uma invisibilidade perversa, que sobrecarrega a mulher e impede o pleno desenvolvimento da cidadania no país.\n\nEm primeira análise, é fundamental destacar que a \"dupla jornada\" é fruto de um silenciamento estrutural. De acordo com o IBGE, as mulheres dedicam quase o dobro de tempo que os homens às tarefas domésticas. Essa disparidade não é apenas estatística, mas sintoma de um Brasil que ainda herda o conceito de \"anjo do lar\" do século XIX, em que o espaço público pertence ao homem e o privado à mulher. Enquanto o trabalho produtivo (remunerado) é valorizado, o trabalho reprodutivo — essencial para o funcionamento da economia — é tratado como um \"dom\" ou \"dever natural\", sendo desprovido de reconhecimento financeiro ou social.\n\nAdemais, a ausência de políticas públicas eficazes agrava o cenário. A falta de vagas em creches e centros de assistência a idosos força a mulher a abdicar de sua carreira ou estudos para suprir lacunas que deveriam ser preenchidas pelo Estado. Segundo a teoria do \"Fato Social\" de Durkheim, o comportamento individual é condicionado por normas coercitivas da sociedade. Assim, a pressão social para que a mulher seja a principal cuidadora torna-se uma barreira invisível, porém intransponível, que perpetua a desigualdade de gênero e a pobreza feminina.\n\nPortanto, medidas são necessárias para mitigar essa invisibilidade. Cabe ao Ministério da Educação, em parceria com o Ministério das Mulheres, promover a desconstrução de estereótipos de gênero desde o ensino básico. Isso deve ser feito por meio da revisão de materiais didáticos e da realização de palestras que incentivem a divisão equitativa das tarefas domésticas entre meninos e meninas. Paralelamente, o Governo Federal deve ampliar o investimento em infraestrutura de apoio, como creches em tempo integral, para que o cuidado deixe de ser um fardo individual e passe a ser uma responsabilidade coletiva. Somente assim, a educação, como previa Kant, transformará o homem e a sociedade em um ambiente de equidade."
    },
    {
        "nota_oficial": 960,
        "nome": "960 - More/Bauman",
        "tema": "Os impactos do descarte inadequado de lixo eletrônico no meio ambiente brasileiro",
        "texto": "Na obra \"Utopia\", de Thomas More, é descrita uma sociedade ideal onde os problemas sociais foram sanados. Contudo, a realidade brasileira contemporânea distancia-se desse ideal ao negligenciar o manejo do lixo eletrônico. Com o avanço tecnológico acelerado e a obsolescência programada, o descarte incorreto de dispositivos tornou-se um desafio ambiental e de saúde pública de proporções alarmantes.\n\nSob esse viés, a lógica do consumo desenfreado impulsiona a problemática. A indústria tecnológica, pautada no lucro imediato, produz equipamentos com vida útil reduzida, forçando o consumidor à substituição constante. Esse ciclo, analisado pelo sociólogo Zygmunt Bauman como \"Modernidade Líquida\", reflete uma sociedade onde tudo é descartável, inclusive o meio ambiente. Metais pesados, como chumbo e mercúrio, presentes nesses componentes, contaminam o solo e os lençóis freáticos quando depositados em lixões comuns, afetando a biodiversidade e a saúde humana.\n\nOutrossim, a falta de informação da população sobre a logística reversa impede o progresso. Embora a Política Nacional de Resíduos Solidos estabeleça diretrizes para o retorno desses produtos aos fabricantes, a maioria dos cidadãos desconhece os pontos de coleta ou a importância desse processo. Dessa forma, o e-lixo acaba acumulado em residências ou descartado de forma mista com resíduos orgânicos, inviabilizando a reciclagem especializada.\n\nLogo, urge que o Ministério do Meio Ambiente, em colaboração com as empresas de tecnologia, amplie os postos de coleta seletiva para resíduos eletrônicos em centros urbanos. Essas empresas devem ser incentivadas, através de benefícios fiscais, a implementar programas de recompra ou descontos para quem entrega aparelhos antigos. Além disso, campanhas publicitárias de grande alcance devem esclarecer os riscos do descarte incorreto. Com essas ações, o Brasil poderá caminhar para mais próximo da utopia de More, garantindo um ambiente equilibrado para as gerações futuras."
    },
    {
        "nota_oficial": 840,
        "nome": "840 - Aristóteles",
        "tema": "A importância do voluntariado para a construção de uma sociedade mais solidária",
        "texto": "O voluntariado é um ato de cidadania que ajuda muito no desenvolvimento do país. No Brasil, muitas pessoas precisam de ajuda e as ONGs fazem um trabalho que o governo muitas vezes não consegue fazer sozinho. É importante entender como essa prática ajuda a criar união entre as pessoas e resolve problemas sociais graves.\n\nEm primeiro lugar, o trabalho voluntário desenvolve a empatia. Quando um indivíduo sai da sua zona de conforto para ajudar o próximo, ele passa a ver a realidade de forma diferente. Segundo o pensamento de Aristóteles, a base da sociedade é a busca pelo bem comum. O voluntariado é a prova prática disso, pois une diferentes classes sociais em torno de um objetivo único: ajudar quem tem fome ou quem não tem acesso à educação.\n\nPor outro lado, o Brasil ainda tem poucos voluntários se comparado a outros países. Isso acontece porque não existe uma cultura de incentivo desde a escola. Muitas pessoas querem ajudar, mas não sabem por onde começar ou acham que precisam de muito dinheiro para ser voluntário, o que é um erro, já que o tempo é o recurso mais valioso. Sem o incentivo correto, o potencial de mudança social acaba sendo desperdiçado.\n\nPortanto, para melhorar esse cenário, o Ministério da Educação deve criar projetos nas escolas que incentivem os alunos a participarem de atividades comunitárias. Isso pode ser feito através de horas complementares ou projetos de extensão que valham nota. Também é papel da mídia divulgar histórias de sucesso de voluntários para inspirar mais gente. Assim, a sociedade brasileira será mais justa e solidária para todos."
    },
    {
        "nota_oficial": 680,
        "nome": "680 - Educação Financeira",
        "tema": "O desafio da educação financeira na formação dos jovens brasileiros",
        "texto": "No Brasil, a educação financeira é um assunto que pouco se fala nas escolas e dentro das famílias. A Constituição Federal de 1988 garante o direito à educação para todos, mas na prática, muitos jovens saem do ensino médio sem saber como cuidar do próprio dinheiro. Isso gera um problema grave, pois o endividamento cresce cada vez mais entre a população jovem que não sabe se planejar para o futuro.\n\nEm primeiro lugar, é importante destacar que o sistema de ensino brasileiro foca muito em matérias teóricas e deixa de lado o ensino prático sobre finanças. O filósofo Immanuel Kant diz que o homem é o que a educação faz dele. Sendo assim, se o jovem não aprende sobre juros, poupança e investimentos na escola, ele terá muita dificuldade em lidar com o seu salário quando entrar no mercado de trabalho. Sem essa base, é comum que muitos acabem gastando mais do que ganham, entrando no cheque especial e no cartão de crédito logo cedo.\n\nAlém disso, vivemos em uma sociedade de consumo que incentiva o tempo todo a compra de produtos novos, muitas vezes por influência das redes sociais. Os jovens são os que mais sofrem com essa pressão, pois querem ter o celular da moda ou roupas caras para se sentirem aceitos no grupo. Como não existe um pensamento crítico sobre o consumo consciente, o desejo de comprar fala mais alto que a necessidade de economizar. Isso mostra que o desafio não é só saber matemática, mas sim mudar o comportamento diante do dinheiro.\n\nPortanto, medidas são necessárias para mudar essa realidade. O Ministério da Educação deve incluir a educação financeira como uma matéria obrigatória na grade curricular das escolas, por meio de aulas práticas e projetos que ensinem os alunos a economizar. Também é papel das famílias conversar mais sobre o orçamento da casa com os filhos. Com essas ações, o Brasil poderá ter jovens mais preparados para cuidar do seu dinheiro e evitar o superendividamento, garantindo uma vida mais tranquila e organizada para todos."
    },
    {
        "nota_oficial": 620,
        "nome": "620 - Sedentarismo",
        "tema": "Os desafios do combate ao sedentarismo na era digital",
        "texto": "Atualmente o sedentarismo é um problema muito grande no Brasil porque as pessoas ficam muito tempo no celular e no computador. Isso faz com que elas não façam exercícios físicos e acabam tendo doenças como obesidade e problemas no coração. É preciso mudar isso para a saúde melhorar.\n\nMuitos jovens passam horas jogando videogame ou nas redes sociais e esquecem de praticar esportes. Antigamente as crianças brincavam na rua, mas hoje a tecnologia mudou tudo. Isso é ruim porque o corpo precisa se mexer. Além disso, a comida rápida (fast food) também ajuda a engordar, e junto com a falta de exercício, vira um perigo para a vida de todo mundo.\n\nOutra coisa é que as academias são caras e nem todo mundo tem dinheiro para pagar. O governo deveria fazer mais parques e lugares para as pessoas caminharem de graça. Se tivesse mais incentivo, com certeza o povo ia se exercitar mais e ir menos aos hospitais, que já estão sempre lotados.\n\nPara resolver o problema, o governo deve investir em esportes nas escolas e nos bairros. Criar campanhas falando que exercício é bom para a saúde. Também as empresas podem dar um tempo para os funcionários se alongarem. Assim o sedentarismo vai diminuir no futuro."
    },
    {
        "nota_oficial": 540,
        "nome": "540 - Redes Sociais",
        "tema": "A influência das redes sociais na vida dos jovens brasileiros",
        "texto": "As rede social hoje em dia manda na vida de muita gente principalmente dos jovens. Eles fica o dia todo olhando a vida dos outros e as vezes fica triste por que queria ter aquela vida de luxo que aparece no Instagram. Isso causa muita depressão e ansiedade nos adolescente.\n\nEu acho que a rede social tem o lado bom e o lado ruim. O lado bom é que você fala com quem mora longe e aprende coisas novas. O lado ruim é o bullying que acontece muito e as fakenews que as pessoas acredita e espalha sem saber se é verdade. Muita gente usa as rede social pra atacar os outros e isso não é certo.\n\nAs famílias tem que olhar o que os filhos faz na internet. Por que tem muitos perigos e pessoas ruins querendo enganar os jovens. Os pais precisa ter mais controle e conversar mais com os filhos sobre os perigo da rede social e não deixar eles ficar tanto tempo no celular.\n\nPra resolver isso as escolas tem que dar palestras e o governo fazer leis mais forte contra o crime na internet. Se todo mundo ajudar, os jovens vai usar a internet de um jeito melhor e não vai ter tantos problemas de saúde mental igual hoje em dia."
    }
]

def enviar_redacao(redacao):
    """Envia uma redação para correção"""
    payload = {
        "tema": redacao["tema"],
        "texto_redacao": redacao["texto"]
    }
    try:
        resp = requests.post(BASE_URL, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, json=payload)
        return resp.json()
    except Exception as e:
        return {"id": None, "error": str(e)}

def consultar_resultado(redacao_id):
    """Consulta o resultado de uma redação"""
    try:
        resp = requests.get(f"{BASE_URL}{redacao_id}", headers={"Authorization": f"Bearer {TOKEN}"})
        return resp.json()
    except Exception as e:
        return {"status": "ERRO", "error": str(e)}

def main():
    print("="*80)
    print(f"TESTE COMPLETO DE PRECISÃO - {len(REDACOES)} REDAÇÕES")
    print("="*80)
    
    # Enviar redações
    print("\n[FASE 1] Enviando redações...")
    ids = []
    for i, red in enumerate(REDACOES, 1):
        print(f"  Enviando {i}/{len(REDACOES)}: {red['nome']} (Nota {red['nota_oficial']})...", end=" ", flush=True)
        result = enviar_redacao(red)
        rid = result.get('id')
        if rid:
            ids.append((rid, red['nota_oficial'], red['nome']))
            print(f"✓ ID: {rid}")
        else:
            print(f"✗ Erro: {result}")
        time.sleep(1) # Pequeno delay para não sobrecarregar
    
    # Aguardar processamento
    tempo_espera = 150 # 2m30s para garantir
    print(f"\n[FASE 2] Aguardando {tempo_espera} segundos para processamento das {len(ids)} redações...")
    time.sleep(tempo_espera)
    
    # Coletar resultados
    print("\n" + "="*80)
    print("RESULTADOS DO TESTE")
    print("="*80)
    
    resultados = []
    
    print(f"{'NOME':<30} | {' ID':<4} | {'OFICIAL':<7} | {'IA':<7} | {'DIFF':<5} | {'STATUS'}")
    print("-" * 80)
    
    for rid, nota_oficial, nome in ids:
        data = consultar_resultado(rid)
        
        if data.get('status') == 'CONCLUIDO':
            # Verificar se resultado_json existe
            res_json = data.get('resultado_json')
            if res_json:
                nota_ia = res_json.get('nota_final', 0)
                diff = nota_ia - nota_oficial
                
                # Check discrepância (pra ver se o sistema de banca funcionou)
                detalhes = res_json.get('detalhes', [])
                num_corretores = len(detalhes)
                info_banca = f"({num_corretores} corr)"
                
                if abs(diff) <= 20:
                    status = "✓✓"
                elif abs(diff) <= 40:
                    status = "✓"
                else:
                    status = "⚠️"
                
                print(f"{nome[:30]:<30} | {rid:<4} | {nota_oficial:<7} | {nota_ia:<7} | {diff:+5d} | {status} {info_banca}")
                resultados.append((nota_oficial, nota_ia, diff))
            else:
                print(f"{nome[:30]:<30} | {rid:<4} | {nota_oficial:<7} | {'ERRO':<7} | {'-':<5} | JSON ausente")
        else:
            status_atual = data.get('status', 'ERRO')
            if status_atual == 'PENDENTE' or status_atual == 'PROCESSANDO':
                 # Tenta esperar um pouco mais para essa específica se estiver pendente
                 print(f"{nome[:30]:<30} | {rid:<4} | {nota_oficial:<7} | {'...':<7} | {'-':<5} | Still {status_atual}")
            else:
                 print(f"{nome[:30]:<30} | {rid:<4} | {nota_oficial:<7} | {'FALHA':<7} | {'-':<5} | {status_atual}")

    # Estatísticas
    if resultados:
        print("\n" + "="*80)
        print("ESTATÍSTICAS FINAIS")
        print("="*80)
        diffs = [abs(r[2]) for r in resultados]
        ideal = sum(1 for d in diffs if d <= 20)
        aceitavel = sum(1 for d in diffs if d <= 40)
        
        print(f"Total Analisado: {len(diffs)}")
        print(f"Desvio Médio Absoluto: {sum(diffs)/len(diffs):.1f} pontos")
        print(f"Meta Ideal (±20): {ideal}/{len(diffs)} ({ideal/len(diffs)*100:.0f}%)")
        print(f"Meta Aceitável (±40): {aceitavel}/{len(diffs)} ({aceitavel/len(diffs)*100:.0f}%)")
        
        # Verificar se as notas baixas ainda são o problema
        print("\nAnálise por Faixa:")
        for off, ia, df in resultados:
            flag = "⚠️" if abs(df) > 40 else "✓"
            print(f"  Nota {off}: Erro de {df:+d} {flag}")
            
        print("="*80)

if __name__ == "__main__":
    main()
