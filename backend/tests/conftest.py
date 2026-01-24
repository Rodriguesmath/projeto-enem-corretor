import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

# Adiciona o diretório raiz (/app) ao sys.path para importações funcionarem como 'backend.main'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Alternativa robusta para Docker:
if "/app" not in sys.path:
    sys.path.append("/app")

from backend.main import app
from backend.core.database import get_db
from shared.models import Base
from backend.celery_app import celery_app

# SQLite em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Cria um banco novo a cada teste.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Cliente de teste com override de dependência de banco.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_celery(monkeypatch):
    """
    Mock do Celery para não depender de Redis.
    """
    mock_send_task = MagicMock()
    monkeypatch.setattr(celery_app, "send_task", mock_send_task)
    return mock_send_task
