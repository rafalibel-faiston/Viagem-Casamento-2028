# Viagem de Casamento 2028 — Rafa & Vitória

App fullstack (FastAPI + Postgres) pra vocês dois organizarem destinos, referências e a grana da viagem em vez de festa. Sem login — só o link do Railway, autor escolhido por um toggle (Rafa/Vitória) salvo no navegador.

## 1. Organize os arquivos assim

Os arquivos vieram todos "achatados" na pasta de output (limitação da ferramenta de arquivos aqui). Antes de subir pro GitHub/Railway, organize num repo com esta estrutura:

```
viagem-app/
├── main.py              (era viagem-app-main.py)
├── database.py           (era viagem-app-database.py)
├── models.py              (era viagem-app-models.py)
├── schemas.py             (era viagem-app-schemas.py)
├── requirements.txt       (era viagem-app-requirements.txt)
├── Procfile               (era viagem-app-Procfile)
├── .gitignore              (era viagem-app-gitignore.txt)
├── .env.example            (era viagem-app-env-example.txt)
└── frontend/
    └── index.html          (era viagem-app-frontend-index.html)
```

Só renomear e mover o `frontend-index.html` pra dentro de uma pasta `frontend/`. O resto fica na raiz.

## 2. Rodar local antes de subir (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Sem `DATABASE_URL` configurada, ele cai automaticamente num SQLite local (`local.db`) — dá pra testar tudo sem precisar de Postgres. Abre `http://localhost:8000`.

Não consegui rodar isso de fato aqui no sandbox (ambiente Linux caiu no meio da sessão), então revisei o código manualmente com calma, mas vale rodar local antes de confiar de olhos fechados.

## 3. Deploy no Railway

1. Sobe a pasta `viagem-app/` num repo novo no GitHub.
2. No Railway: **New Project → Deploy from GitHub repo**, aponta pro repo.
3. **Add a service → Database → PostgreSQL** (addon nativo do Railway).
4. No serviço do app (não no do banco), vai em **Variables** e adiciona:
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   ```
   (o Railway resolve essa referência sozinho e injeta a URL real do banco que você acabou de criar)
5. O Railway detecta Python automaticamente (Nixpacks) e usa o `Procfile` pra subir com `uvicorn`. Não precisa mexer em mais nada.
6. Gera o domínio público em **Settings → Networking → Generate Domain**.

Na primeira subida, o `main.py` cria as tabelas (`Base.metadata.create_all`) e popa os 8 destinos + os 3 passos do checklist automaticamente — só roda se as tabelas estiverem vazias, então é seguro fazer redeploy depois sem duplicar nada.

## 4. O que o app faz

- **Destinos**: os 8 lugares já organizados em 3 tiers, com botão de curtir — o coração mostra quem já votou.
- **Mural de referências**: cada um posta link, ideia ou texto solto, com comentários embaixo.
- **Calculadora**: orçamento, renda combinada e data do casamento ficam salvos no banco — abre em qualquer navegador e está sincronizado pros dois.
- **Checklist**: os 3 próximos passos iniciais, mais o que forem adicionando.

## 5. Próximas melhorias possíveis (se quiser evoluir depois)

- Trocar o toggle de autor por auth de verdade (nem que seja magic link) se um dia quiser deixar mais gente ver.
- Migrations com Alembic em vez de `create_all` direto, se o schema for crescer.
- Upload de imagem real no mural (hoje só aceita link/texto) — precisaria de storage tipo S3/R2, o Railway não guarda arquivo estático de upload de forma persistente.
