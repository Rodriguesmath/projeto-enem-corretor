from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from shared.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    redacoes = relationship("Redacao", back_populates="owner")


class Redacao(Base):
    __tablename__ = "redacoes"

    id = Column(Integer, primary_key=True, index=True)
    tema = Column(String, index=True)
    texto_redacao = Column(Text, nullable=False)
    status = Column(String, default="PENDENTE")
    resultado_json = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="redacoes")



