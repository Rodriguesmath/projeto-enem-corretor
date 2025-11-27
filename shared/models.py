from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está configurada!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Redacao(Base):
    __tablename__ = "redacoes"

    id = Column(Integer, primary_key=True, index=True)
    tema = Column(String, index=True)
    texto_redacao = Column(Text, nullable=False)
    status = Column(String, default="PENDENTE")
    resultado_json = Column(JSON, nullable=True)


Base.metadata.create_all(bind=engine)
