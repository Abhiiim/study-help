# Study Saver Server

FastAPI backend for authentication, saved items, and link parsing.

## Prerequisites

- Python 3.11+
- PostgreSQL running locally

## Setup

```bash
cd apps/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your database and auth settings. The default database URL is:

```env
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/study_saver"
```

Create the `study_saver` database in PostgreSQL before starting the API.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`. API routes are under `http://localhost:8000/api/v1`.

## Test

```bash
pytest
```
