#!/usr/bin/env python3
"""
Teste Focado - Redações Baixas (<600)
"""
import requests
import json
import time

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZV9maW5hbEBleGVtcGxvLmNvbSIsImV4cCI6MTc2OTMxMTA2Nn0.7p52IpdNKXFpOrVVVbIns89QFaw3VJMtBnN-I4Nbq8k"
BASE_URL = "http://localhost:8000/api/v1/redacoes/"

REDACOES_BAIXAS = [
    {
        "nota_oficial": 520,
        "nome": "520 - Animais",
        "tema": "O abandono de animais domésticos nas cidades brasileiras",
        "texto": "O abandono de animais é uma coisa muito triste que acontece muito no Brasil. Muita gente pega um cachorro ou gato quando é pequeno e bonitinho, mas quando cresce ou dá gastos eles abandonam na rua. Isso é um crime e faz mal para os bichos e para a saúde das pessoas também.\n\nNa rua os animais podem pegar doenças e passar para os humanos, como a raiva. Além disso, eles sofrem muito com fome e frio. As prefeituras não fazem quase nada para ajudar, os abrigos estão sempre cheios e não tem dinheiro para cuidar de todos. Falta castração gratuita para os animais não procriarem na rua sem controle nenhum.\n\nEu acho que as pessoas deviam ter mais responsabilidade. Ter um animal não é um brinquedo, é uma vida. Se a pessoa não tem condições, não deve pegar para depois jogar fora. Muitas vezes os animais são maltratados antes de serem abandonados e isso é muita crueldade.\n\nPara melhorar isso, o governo tem que dar multas pesadas para quem abandona e fazer campanhas de adoção. As escolas também podem falar sobre cuidar dos animais. Assim vamos ter menos animais sofrendo nas ruas e a cidade vai ser mais limpa e segura."
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
    payload = {"tema": redacao["tema"], "texto_redacao": redacao["texto"]}
    try:
        resp = requests.post(BASE_URL, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, json=payload)
        return resp.json()
    except Exception as e:
        return {"id": None, "error": str(e)}

def consultar_resultado(redacao_id):
    try:
        resp = requests.get(f"{BASE_URL}{redacao_id}", headers={"Authorization": f"Bearer {TOKEN}"})
        return resp.json()
    except:
        return {}

def main():
    print("="*60)
    print("TESTE FOCADO - NOTAS BAIXAS (<600)")
    print("="*60)
    
    ids = []
    for red in REDACOES_BAIXAS:
        print(f"Enviando {red['nome']}...", end=" ", flush=True)
        res = enviar_redacao(red)
        rid = res.get('id')
        if rid:
            ids.append((rid, red['nota_oficial'], red['nome']))
            print(f"✓ ID: {rid}")
        else:
            print("✗ Erro")
        time.sleep(1)
        
    print("\nAguardando 90 segundos...")
    time.sleep(90)
    
    print("\n" + "="*60)
    print("RESULTADOS DO TESTE DE PISO")
    print("="*60)
    
    for rid, nota_oficial, nome in ids:
        data = consultar_resultado(rid)
        if data.get('status') == 'CONCLUIDO':
            # Verificar se resultado_json existe
            res_json = data.get('resultado_json')
            if res_json:
                nota_ia = res_json['nota_final']
                diff = nota_ia - nota_oficial
                status = "✓" if abs(diff) <= 60 else "⚠️"
                print(f"{status} {nome:20s} | Oficial: {nota_oficial} → IA: {nota_ia} ({diff:+d})")
                
                # Mostrar competências para debug
                comps = res_json.get('competencias', [])
                c_str = " | ".join([f"C{i+1}:{c['nota']}" for i, c in enumerate(comps)])
                print(f"   {c_str}")
            else:
                 print(f"⚠️ {nome:20s} | Oficial: {nota_oficial} → IA: ??? (JSON ausente)")
        else:
            print(f"⏳ {nome:20s} | Status: {data.get('status')}")

if __name__ == "__main__":
    main()
