from shared.schemas import RedacaoStatusEnum

def get_auth_token(client, email="user@test.com"):
    client.post("/register", json={"email": email, "password": "pass"})
    response = client.post("/token", data={"username": email, "password": "pass"})
    return response.json()["access_token"]

def test_submit_essay(client, mock_celery):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/redacoes/", 
        json={"tema": "Enem", "texto_redacao": "Teste"},
        headers=headers
    )
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == RedacaoStatusEnum.PENDENTE
    
    # Verifica se o Celery foi chamado
    mock_celery.assert_called_once()
    assert mock_celery.call_args[0][0] == "correct_essay"
    assert mock_celery.call_args[1]["args"][0] == data["id"]

def test_list_essays(client):
    token = get_auth_token(client, email="list@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submete 2 redações
    client.post("/api/v1/redacoes/", json={"tema": "T1", "texto_redacao": "R1"}, headers=headers)
    client.post("/api/v1/redacoes/", json={"tema": "T2", "texto_redacao": "R2"}, headers=headers)
    
    response = client.get("/api/v1/redacoes/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_security_access_other_user_essay(client):
    # User 1 cria redação
    token1 = get_auth_token(client, email="u1@test.com")
    headers1 = {"Authorization": f"Bearer {token1}"}
    resp = client.post("/api/v1/redacoes/", json={"tema": "T", "texto_redacao": "R"}, headers=headers1)
    redacao_id = resp.json()["id"]
    
    # User 2 tenta acessar
    token2 = get_auth_token(client, email="u2@test.com")
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    response = client.get(f"/api/v1/redacoes/{redacao_id}", headers=headers2)
    assert response.status_code == 404 # Ou 403, dependendo da implementação (neste caso 404 para não vazar ID)

def test_submit_empty_essay(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/redacoes/", 
        json={"tema": "T"}, # Faltando texto_redacao
        headers=headers
    )
    assert response.status_code == 422
