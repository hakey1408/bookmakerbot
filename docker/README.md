# Docker — Come usare

## Prerequisiti
- Docker e Docker Compose installati.
- Un file `.env` nella root del progetto con le variabili necessarie (vedi `.env.example`).

## Servizi inclusi
- `db`: PostgreSQL con database `RicashDB`
- `bot`: bot Telegram Python collegato al database

## Build e avvio

```bash
# Dalla cartella docker/
cd docker
docker compose up --build -d
```

## Fermare i servizi

```bash
cd docker
docker compose down
```

## Logs

```bash
cd docker
docker compose logs -f db
cd docker
docker compose logs -f bot
```

## Verifica rapida del database

```bash
cd docker
docker compose exec db psql -U ricash -d RicashDB -c 'SELECT id, nome, priorita, attivo FROM "Bookmakers" ORDER BY id;'
```
