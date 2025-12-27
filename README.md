# kazuko_departure_watch

Departure monitoring system powered by FastAPI.

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in values.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Tests

```bash
pytest
```
