from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Viagem de Casamento — Rafa & Vitória")


# ---------------------------------------------------------------------------
# Seed inicial (só roda se as tabelas estiverem vazias — idempotente)
# ---------------------------------------------------------------------------
SEED_DESTINOS = [
    dict(
        tier=1, ordem=0, nome="Chapada Diamantina, BA",
        descricao="Cachoeiras, cânions e poços de água cristalina como o Poço Azul. "
                   "Base em Lençóis ou Vale do Capão, trilha o dia todo.",
        custo_min=6500, custo_max=8500, dias="10 dias", icon_key="wave",
    ),
    dict(
        tier=1, ordem=1, nome="Jericoacoara + Delta do Parnaíba",
        descricao="Dunas e lagoas em Jeri combinadas com o único delta de mar aberto "
                   "das Américas, de jangada entre os três rios.",
        custo_min=7000, custo_max=9000, dias="10 dias", icon_key="dune",
    ),
    dict(
        tier=1, ordem=2, nome="Alter do Chão, PA",
        descricao='O "Caribe da Amazônia": praia de água doce, floresta ao redor, '
                   "encontro dos rios. Autêntico e muito mais barato.",
        custo_min=6000, custo_max=7500, dias="10 dias", icon_key="tree",
    ),
    dict(
        tier=1, ordem=3, nome="Bonito, MS",
        descricao="Flutuação em rios de água transparente, grutas e ecoturismo de "
                   "altíssimo nível. Passeios têm preço fixo, mas valem cada real.",
        custo_min=8000, custo_max=10000, dias="10 dias", icon_key="river",
    ),
    dict(
        tier=2, ordem=0, nome="Cartagena + Tayrona + La Guajira",
        descricao="Cidade histórica colorida, selva caindo no Caribe (Tayrona) e "
                   "deserto batendo na costa (Guajira) — combo raro de fazer.",
        custo_min=13000, custo_max=16000, dias="12–14 dias", icon_key="globe",
    ),
    dict(
        tier=2, ordem=1, nome="Litoral selvagem do Uruguai",
        descricao="Cabo Polonio (só se chega de trator pela duna) e Punta del Diablo, "
                   "clima hippie, longe do circuito Punta del Este.",
        custo_min=10500, custo_max=13000, dias="10–12 dias", icon_key="wave",
    ),
    dict(
        tier=2, ordem=2, nome="Huacachina + Paracas, Peru",
        descricao='Oásis no deserto com sandboard e buggy, e as Ilhas Ballestas — o '
                   '"Galápagos dos pobres", cheio de lobos-marinhos e pinguins.',
        custo_min=11500, custo_max=14500, dias="12 dias", icon_key="dune",
    ),
    dict(
        tier=3, ordem=0, nome="Cabo Verde",
        descricao="Ilhas vulcânicas na costa da África, praias, trilhas e morna ao "
                   "vivo. Voo direto Recife → Praia, sem escala pela Europa.",
        custo_min=17000, custo_max=20000, dias="10–12 dias", icon_key="compass",
    ),
]

SEED_CHECKLIST = [
    "Fechar a data (mesmo aproximada) do casamento em 2028",
    "Escolher o destino ou dois finalistas pra comparar preço de voo",
    "Abrir a reserva separada (CDB liquidez diária ou Tesouro Selic) com aporte automático",
]


@app.on_event("startup")
def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(models.Destino).count() == 0:
            db.add_all(models.Destino(**d) for d in SEED_DESTINOS)
        if db.query(models.ChecklistItem).count() == 0:
            db.add_all(
                models.ChecklistItem(texto=t, ordem=i)
                for i, t in enumerate(SEED_CHECKLIST)
            )
        if db.query(models.OrcamentoConfig).count() == 0:
            db.add(models.OrcamentoConfig())
        db.commit()
    finally:
        db.close()


def serialize_destino(d: models.Destino) -> schemas.DestinoOut:
    return schemas.DestinoOut(
        id=d.id,
        tier=d.tier,
        nome=d.nome,
        descricao=d.descricao,
        custo_min=d.custo_min,
        custo_max=d.custo_max,
        dias=d.dias,
        icon_key=d.icon_key,
        votos=[v.autor for v in d.votos],
    )


# ---------------------------------------------------------------------------
# Destinos + votação
# ---------------------------------------------------------------------------
@app.get("/api/destinos", response_model=list[schemas.DestinoOut])
def listar_destinos(db: Session = Depends(get_db)):
    destinos = db.query(models.Destino).order_by(models.Destino.tier, models.Destino.ordem).all()
    return [serialize_destino(d) for d in destinos]


@app.post("/api/destinos/{destino_id}/votar", response_model=schemas.DestinoOut)
def votar_destino(destino_id: int, payload: schemas.VotarIn, db: Session = Depends(get_db)):
    destino = db.get(models.Destino, destino_id)
    if not destino:
        raise HTTPException(404, "Destino não encontrado")

    existente = (
        db.query(models.VotoDestino)
        .filter_by(destino_id=destino_id, autor=payload.autor)
        .first()
    )
    if existente:
        db.delete(existente)
    else:
        db.add(models.VotoDestino(destino_id=destino_id, autor=payload.autor))
    db.commit()
    db.refresh(destino)
    return serialize_destino(destino)


# ---------------------------------------------------------------------------
# Mural de referências + comentários
# ---------------------------------------------------------------------------
@app.get("/api/mural", response_model=list[schemas.MuralItemOut])
def listar_mural(db: Session = Depends(get_db)):
    return (
        db.query(models.MuralItem)
        .order_by(models.MuralItem.created_at.desc())
        .all()
    )


@app.post("/api/mural", response_model=schemas.MuralItemOut)
def criar_mural(payload: schemas.MuralItemIn, db: Session = Depends(get_db)):
    item = models.MuralItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/mural/{item_id}")
def deletar_mural(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.MuralItem, item_id)
    if not item:
        raise HTTPException(404, "Item não encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.post("/api/mural/{item_id}/comentarios", response_model=schemas.ComentarioOut)
def comentar(item_id: int, payload: schemas.ComentarioIn, db: Session = Depends(get_db)):
    mural = db.get(models.MuralItem, item_id)
    if not mural:
        raise HTTPException(404, "Post não encontrado")
    c = models.Comentario(mural_id=item_id, **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ---------------------------------------------------------------------------
# Checklist
# ---------------------------------------------------------------------------
@app.get("/api/checklist", response_model=list[schemas.ChecklistItemOut])
def listar_checklist(db: Session = Depends(get_db)):
    return db.query(models.ChecklistItem).order_by(models.ChecklistItem.ordem).all()


@app.post("/api/checklist", response_model=schemas.ChecklistItemOut)
def criar_checklist(payload: schemas.ChecklistItemIn, db: Session = Depends(get_db)):
    maior_ordem = db.query(models.ChecklistItem).count()
    item = models.ChecklistItem(
        texto=payload.texto, criado_por=payload.criado_por, ordem=maior_ordem
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/api/checklist/{item_id}", response_model=schemas.ChecklistItemOut)
def atualizar_checklist(
    item_id: int, payload: schemas.ChecklistItemUpdate, db: Session = Depends(get_db)
):
    item = db.get(models.ChecklistItem, item_id)
    if not item:
        raise HTTPException(404, "Item não encontrado")
    if payload.feito is not None:
        item.feito = payload.feito
    if payload.texto is not None:
        item.texto = payload.texto
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/checklist/{item_id}")
def deletar_checklist(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.ChecklistItem, item_id)
    if not item:
        raise HTTPException(404, "Item não encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Orçamento (linha única, persiste o que a calculadora usa)
# ---------------------------------------------------------------------------
@app.get("/api/orcamento", response_model=schemas.OrcamentoOut)
def get_orcamento(db: Session = Depends(get_db)):
    cfg = db.query(models.OrcamentoConfig).first()
    if not cfg:
        cfg = models.OrcamentoConfig()
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@app.put("/api/orcamento", response_model=schemas.OrcamentoOut)
def set_orcamento(payload: schemas.OrcamentoIn, db: Session = Depends(get_db)):
    cfg = db.query(models.OrcamentoConfig).first()
    if not cfg:
        cfg = models.OrcamentoConfig()
        db.add(cfg)
    cfg.orcamento_total = payload.orcamento_total
    cfg.renda_combinada = payload.renda_combinada
    cfg.data_casamento = payload.data_casamento
    db.commit()
    db.refresh(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Frontend estático (precisa ser montado por último, é um catch-all em "/")
# ---------------------------------------------------------------------------
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
