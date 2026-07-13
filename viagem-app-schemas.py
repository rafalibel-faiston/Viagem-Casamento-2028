from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DestinoOut(BaseModel):
    id: int
    tier: int
    nome: str
    descricao: str
    custo_min: int
    custo_max: int
    dias: str
    icon_key: str
    votos: List[str] = []

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class OrcamentoIn(BaseModel):
    orcamento_total: int
    renda_combinada: int
    data_casamento: str
