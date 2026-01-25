#!/usr/bin/env python3
"""
Teste Completo de Precisão - 8 Redações (920 a 240)
"""

import requests
import json
import time

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZV9maW5hbEBleGVtcGxvLmNvbSIsImV4cCI6MTc2OTMxMTA2Nn0.7p52IpdNKXFpOrVVVbIns89QFaw3VJMtBnN-I4Nbq8k"
BASE_URL = "http://localhost:8000/api/v1/redacoes/"

REDACOES = [
    {
        "nota_oficial": 920,
        "nome": "920 - Aristóteles/Locke",
        "tema": "A democratização do acesso ao esporte como ferramenta de inclusão social",
        "texto": "O filósofo grego Aristóteles defendia que a política deve visar o bem-estar coletivo. No entanto, a realidade brasileira contemporânea apresenta um entrave à plena cidadania: a dificuldade de acesso ao esporte por camadas vulneráveis da população. Essa problemática é fruto de uma negligência estatal histórica aliada à percepção equivocada do desporto como mero lazer, o que invisibiliza seu potencial transformador.\n\nEm primeira análise, a precariedade da infraestrutura esportiva em regiões periféricas atua como um mecanismo de exclusão. Segundo o \"Contrato Social\" de John Locke, o Estado deve garantir direitos básicos em troca da ordem social. Contudo, ao falhar na manutenção de quadras públicas e no fomento a projetos sociais esportivos, o poder público priva jovens de alternativas ao crime e à ociosidade. O esporte não é apenas atividade física; é um espaço de aprendizado de regras, respeito e disciplina, fundamentais para o convívio democrático.\n\nAdemais, o viés elitista do esporte profissional dificulta a ascensão de talentos sem recursos. Sem patrocínio ou bolsas de auxílio, muitos atletas desistem de suas carreiras por necessidade de subsistência. Essa lacuna de investimentos reflete uma visão utilitarista da educação, que prioriza apenas o conteúdo técnico e subestima a formação integral do indivíduo através do corpo.\n\nPortanto, urge que o Ministério do Esporte, em parceria com as prefeituras, revitalize centros esportivos comunitários e implemente programas de iniciação desportiva nas escolas públicas de tempo integral. Tais ações devem ser acompanhadas de editais de incentivo a atletas de baixa renda. Somente assim, o esporte deixará de ser um privilégio de poucos e passará a ser a ferramenta de bem-estar e cidadania prevista na teoria aristotélica."
    },
    {
        "nota_oficial": 820,
        "nome": "820 - Orwell/Bauman/IA",
        "tema": "O impacto da inteligência artificial na privacidade do cidadão comum",
        "texto": "Na obra \"1984\", George Orwell retrata uma sociedade sob vigilância constante do \"Grande Irmão\". Fora da ficção, a inteligência artificial (IA) moderna, embora facilite o cotidiano, cria um cenário de monitoramento digital que ameaça a privacidade individual. Esse desafio ocorre devido ao avanço tecnológico descompassado da legislação e à falta de consciência dos usuários sobre o valor de seus dados.\n\nSob esse viés, a coleta massiva de informações por algoritmos de IA é alarmante. Empresas utilizam dados pessoais para traçar perfis psicológicos e influenciar decisões de consumo e até políticas. Segundo o conceito de \"Modernidade Líquida\" de Bauman, as relações são frágeis, e a superexposição digital torna o indivíduo vulnerável a manipulações invisíveis. Sem limites claros, a vida privada torna-se uma mercadoria altamente lucrativa no mercado tecnológico.\n\nOutrossim, a Lei Geral de Proteção de Dados (LGPD) no Brasil é um avanço, mas sua aplicação ainda é insuficiente diante da sofisticação da IA. Muitos cidadãos aceitam termos de uso sem ler, cedendo direitos fundamentais por conveniência.\n\nLogo, é necessário que o Governo Federal amplie a fiscalização sobre empresas de tecnologia, aplicando multas severas em caso de vazamento ou uso indevido de dados. Paralelamente, o Ministério da Educação deve introduzir temas de cidadania digital e proteção de dados no currículo escolar, para que o usuário aprenda a se proteger. Assim, a tecnologia servirá ao homem sem transformá-lo em um vigiado de Orwell."
    },
    {
        "nota_oficial": 740,
        "nome": "740 - Doação de Sangue",
        "tema": "A importância da doação de sangue e os desafios para manter os estoques no Brasil",
        "texto": "A doação de sangue é um ato de solidariedade essencial para o funcionamento do sistema de saúde. Contudo, o Brasil enfrenta dificuldades constantes para manter seus estoques em níveis seguros. Esse problema está ligado à falta de informação de uma parcela da população e também a preconceitos que ainda persistem na sociedade brasileira.\n\nEm princípio, muitos indivíduos deixam de doar por medo ou desconhecimento do processo. Existem mitos de que o sangue pode \"engrossar\" ou de que a pessoa pode se contaminar, o que é falso. De acordo com a Constituição de 1988, a saúde é um direito de todos e dever do Estado, mas a participação popular através da doação é fundamental para que esse direito seja garantido em cirurgias e emergências. Sem campanhas eficazes que desmistifiquem o ato, os hemocentros continuam vazios.\n\nAlém disso, o preconceito contra certos grupos sociais, que historicamente foram impedidos de doar, ainda gera reflexos na baixa adesão. Embora as leis tenham mudado, o estigma permanece. É preciso que a doação seja vista como um dever cívico desvinculado de julgamentos morais.\n\nDessa forma, o Ministério da Saúde deve intensificar as campanhas publicitárias, usando as redes sociais para atingir o público jovem e explicar a segurança do procedimento. Também, as empresas poderiam dar incentivos, como folgas extras, para quem comprovar a doação. Com educação e incentivo, os estoques de sangue serão suficientes para atender a quem precisa."
    },
    {
        "nota_oficial": 640,
        "nome": "640 - Desperdício Alimentos",
        "tema": "Os desafios do combate ao desperdício de alimentos no Brasil",
        "texto": "Atualmente, o desperdício de alimentos é um dos maiores problemas do Brasil, visto que milhões de pessoas passam fome todos os dias. Enquanto toneladas de comida vão para o lixo em feiras e supermercados, muitas famílias não têm o que comer. Isso mostra uma grande desigualdade e falta de organização na distribuição dos recursos.\n\nUm dos motivos para isso acontecer é a cultura do \"excesso\". Muitos consumidores compram mais do que precisam e acabam jogando comida fora porque estragou. Além disso, as exigências estéticas para frutas e legumes fazem com que produtos bons, mas \"feios\", sejam descartados antes de chegar ao consumidor. Isso é um erro, pois o valor nutricional é o mesmo. É preciso conscientização para entender que comida não é lixo.\n\nOutro ponto é o transporte e armazenamento, que no Brasil é muito precário. Caminhões sem refrigeração e estradas ruins fazem com que muito alimento se perca no caminho da fazenda até a cidade.\n\nPara resolver, o governo deve criar leis que facilitem a doação de alimentos por parte de mercados e restaurantes, retirando a burocracia. Também, as escolas devem ensinar desde cedo o consumo consciente. Se cada um fizer sua parte, o desperdício vai diminuir e a fome também pode diminuir no país."
    },
    {
        "nota_oficial": 520,
        "nome": "520 - Animais",
        "tema": "O abandono de animais domésticos nas cidades brasileiras",
        "texto": "O abandono de animais é uma coisa muito triste que acontece muito no Brasil. Muita gente pega um cachorro ou gato quando é pequeno e bonitinho, mas quando cresce ou dá gastos eles abandonam na rua. Isso é um crime e faz mal para os bichos e para a saúde das pessoas também.\n\nNa rua os animais podem pegar doenças e passar para os humanos, como a raiva. Além disso, eles sofrem muito com fome e frio. As prefeituras não fazem quase nada para ajudar, os abrigos estão sempre cheios e não tem dinheiro para cuidar de todos. Falta castração gratuita para os animais não procriarem na rua sem controle nenhum.\n\nEu acho que as pessoas deviam ter mais responsabilidade. Ter um animal não é um brinquedo, é uma vida. Se a pessoa não tem condições, não deve pegar para depois jogar fora. Muitas vezes os animais são maltratados antes de serem abandonados e isso é muita crueldade.\n\nPara melhorar isso, o governo tem que dar multas pesadas para quem abandona e fazer campanhas de adoção. As escolas também podem falar sobre cuidar dos animais. Assim vamos ter menos animais sofrendo nas ruas e a cidade vai ser mais limpa e segura."
    },
    {
        "nota_oficial": 460,
        "nome": "460 - Leitura",
        "tema": "A importância da leitura na formação dos jovens",
        "texto": "A leitura é muito importante para todo mundo pois ajuda a gente a aprender coisas novas e a escrever melhor. Mas hoje em dia os jovens não gostam muito de ler livros por causa da internet e do celular que toma muito tempo. Isso é ruim para o futuro deles.\n\nNas escolas os professores mandam ler livros difíceis e chatos que ninguém entende nada. Aí o aluno pega raiva de ler. Se os livros fossem mais legais e atuais talvez os jovens liam mais. Ler ajuda a pensar melhor e a não acreditar em qualquer coisa que vê por aí na rede social. Quem lê muito tem mais chances de conseguir um emprego bom no futuro porque sabe falar bem.\n\nTambém os pais não dão exemplo. Se o filho não vê o pai lendo ele também não vai querer ler. Livro no Brasil também é muito caro e as bibliotecas são poucas e não tem quase nada de novo.\n\nO governo deveria baixar o preço dos livros e fazer bibliotecas bonitas nos bairros. E as escolas deixar o aluno escolher o que quer ler. Só assim o Brasil vai ser um país de leitores e as pessoas vão ser mais inteligentes."
    },
    {
        "nota_oficial": 380,
        "nome": "380 - Lixo Praias",
        "tema": "O problema do lixo nas praias brasileiras",
        "texto": "O lixo nas praias é um problema que acontece todo verão quando o povo vai viajar. Eles joga latinha, plástico e resto de comida na areia e o mar leva tudo. Isso polui o mar e mata os peixe e as tartarugas que come o plástico pensando que é comida.\n\nÉ muita falta de educação do povo. Tem lixeira na praia mas eles tem preguiça de levantar e jogar o lixo no lugar certo. As praias fica suja e feia e isso é ruim até para o turismo do Brasil. Ninguém quer ir em praia suja. O governo também demora para limpar e o lixo acumula muito.\n\nTem que ter mais fiscalização e prender quem suja a praia. E colocar mais lixeiras grandes. As pessoas tem que levar um saquinho de casa para guardar o lixo delas e não deixar nada na areia. Se todo mundo ajudar a praia fica limpa para o próximo ano."
    },
    {
        "nota_oficial": 240,
        "nome": "240 - TV e Crianças",
        "tema": "A televisão influencia as crianças?",
        "texto": "A televisão passa muita coisa que as crianças não pode ver. Desenhos violentos e propagandas de brinquedos caros que os pais não pode comprar. Isso deixa a criança querendo tudo o que vê e as vezes elas fica brava com os pais por causa disso.\n\nAs crianças fica muito tempo na frente da tv e não quer mais brincar na rua ou estudar. Isso faz elas ficarem gordas e sem saúde. Os pais tem que desligar a tv e levar elas para o parque. A tv ensina coisa errada as vezes e a criança repete o que vê nos programas que não é para a idade delas.\n\nEu acho que a tv é boa para passar notícia mas para criança tem que tomar cuidado. O governo devia proibir certas propagandas de comida ruim e brinquedo na hora dos desenho. Assim as crianças cresce mais saudável."
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
    print(f"TESTE FINAL - 8 REDAÇÕES (920 a 240)")
    print("="*80)
    
    # Enviar redações
    print("\n[FASE 1] Enviando redações...")
    ids = []
    for i, red in enumerate(REDACOES, 1):
        print(f"  Enviando {i}/{len(REDACOES)}: {red['nome']}...", end=" ", flush=True)
        result = enviar_redacao(red)
        rid = result.get('id')
        if rid:
            ids.append((rid, red['nota_oficial'], red['nome']))
            print(f"✓ ID: {rid}")
        else:
            print(f"✗ Erro: {result}")
        time.sleep(1)
    
    # Aguardar processamento
    tempo_espera = 180 # 3 minutos
    print(f"\n[FASE 2] Aguardando {tempo_espera} segundos para processamento...")
    time.sleep(tempo_espera)
    
    # Coletar resultados
    print("\n" + "="*80)
    print("RESULTADOS DO TESTE")
    print("="*80)
    
    resultados = []
    
    print(f"{'NOME':<30} | {'OFICIAL':<7} | {'IA':<7} | {'DIFF':<5} | {'STATUS'}")
    print("-" * 80)
    
    for rid, nota_oficial, nome in ids:
        data = consultar_resultado(rid)
        
        if data.get('status') == 'CONCLUIDO':
            res_json = data.get('resultado_json')
            if res_json:
                nota_ia = res_json.get('nota_final', 0)
                diff = nota_ia - nota_oficial
                
                if abs(diff) <= 20:
                    status = "✓✓"
                elif abs(diff) <= 40:
                    status = "✓"
                else:
                    status = "⚠️"
                
                print(f"{nome[:30]:<30} | {nota_oficial:<7} | {nota_ia:<7} | {diff:+5d} | {status}")
                resultados.append((nota_oficial, nota_ia, diff))
            else:
                print(f"{nome[:30]:<30} | {nota_oficial:<7} | {'ERRO':<7} | {'-':<5} | JSON ausente")
        else:
            print(f"{nome[:30]:<30} | {nota_oficial:<7} | {'...':<7} | {'-':<5} | {data.get('status')}")

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
        
        print("\nAnálise por Faixa:")
        for off, ia, df in resultados:
            flag = "⚠️" if abs(df) > 40 else "✓"
            print(f"  Nota {off}: IA {ia} ({df:+d}) {flag}")
            
        print("="*80)

if __name__ == "__main__":
    main()
