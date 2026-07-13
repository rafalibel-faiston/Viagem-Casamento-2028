from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class TierOut(BaseModel):
    id: int
    nome: str
    ordem: int

    class Config:
        from_attributes = True


class TierIn(BaseModel):
    nome: str


class TierUpdate(BaseModel):
    nome: Optional[str] = None
    ordem: Optional[int] = None


class CustoItemOut(BaseModel):
    id: int
    categoria: str
    descricao: Optional[str] = None
    valor: int
    criado_por: Optional[str] = None

    class Config:
        from_attributes = True


class CustoItemIn(BaseModel):
    categoria: str
    descricao: Optional[str] = None
    valor: int
    autor: Optional[str] = None


class CustosMapIn(BaseModel):
    # {"Passagem": 2500, "Hospedagem": 3000, ...} — substitui todos os custos
    custos: Dict[str, int] = {}
    autor: Optional[str] = None


class DestinoOut(BaseModel):
    id: int
    tier: int
    nome: str
    descricao: str
    custo_min: int
    custo_max: int
    dias: str
    icon_key: str
    criado_por: Optional[str] = None
    votos: List[str] = []
    custos: List[CustoItemOut] = []

    class Config:
        from_attributes = True


class DestinoIn(BaseModel):
    tier: int
    nome: str
    descricao: str
    dias: str
    icon_key: str = "wave"
    custo_min: int = 0
    custo_max: int = 0
    autor: str
    custos: Dict[str, int] = {}  # categoria -> valor, opcional já na criação


class VotarIn(BaseModel):
    autor: str


class ComentarioOut(BaseModel):
    id: int
    autor: str
    texto: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComentarioIn(BaseModel):
    autor: str
    texto: str


class MuralItemOut(BaseModel):
    id: int
    autor: str
    conteudo: str
    created_at: datetime
    comentarios: List[ComentarioOut] = []

    class Config:
        from_attributes = True


class MuralItemIn(BaseModel):
    autor: str
    conteudo: str


class ChecklistItemOut(BaseModel):
    id: int
    texto: str
    feito: bool
    criado_por: Optional[str] = None
    ordem: int

    class Config:
        from_attributes = True


class ChecklistItemIn(BaseModel):
    texto: str
    criado_por: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    feito: Optional[bool] = None
    texto: Optional[str] = None


class OrcamentoOut(BaseModel):
    orcamento_total: int
    renda_combinada: int
    data_casamento: str
    destino_escolhido_id: Optional[int] = None

    class Config:
        from_attributes = True


class OrcamentoIn(BaseModel):
    orcamento_total: int
    renda_combinada: int
    data_casamento: str


class EscolhaIn(BaseModel):
    destino_id: Optional[int] = None  # None = desfazer a escolha
    autor: Optional[str] = None
