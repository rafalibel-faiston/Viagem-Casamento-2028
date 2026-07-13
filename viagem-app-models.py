from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Destino(Base):
    __tablename__ = "destinos"

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(Integer, nullable=False)
    nome = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    custo_min = Column(Integer, nullable=False)
    custo_max = Column(Integer, nullable=False)
    dias = Column(String, nullable=False)
    icon_key = Column(String, nullable=False, default="wave")
    ordem = Column(Integer, default=0)

    votos = relationship(
        "VotoDestino", back_populates="destino", cascade="all, delete-orphan"
    )


class VotoDestino(Base):
    __tablename__ = "votos_destinos"

    id = Column(Integer, primary_key=True, index=True)
    destino_id = Column(Integer, ForeignKey("destinos.id"), nullable=False)
    autor = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    destino = relationship("Destino", back_populates="votos")

    __table_args__ = (
        UniqueConstraint("destino_id", "autor", name="uq_voto_destino_autor"),
    )


class MuralItem(Base):
    __tablename__ = "mural_itens"

    id = Column(Integer, primary_key=True, index=True)
    autor = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comentarios = relationship(
        "Comentario", back_populates="mural_item", cascade="all, delete-orphan"
    )


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    mural_id = Column(Integer, ForeignKey("mural_itens.id"), nullable=False)
    autor = Column(String, nullable=False)
    texto = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mural_item = relationship("MuralItem", back_populates="comentarios")


class ChecklistItem(Base):
    __tablename__ = "checklist_itens"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String, nullable=False)
    feito = Column(Boolean, default=False)
    criado_por = Column(String, nullable=True)
    ordem = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrcamentoConfig(Base):
    __tablename__ = "orcamento_config"

    id = Column(Integer, primary_key=True, index=True)
    orcamento_total = Column(Integer, default=12000)
    renda_combinada = Column(Integer, default=5500)
    data_casamento = Column(String, default="2028-07-01")
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
