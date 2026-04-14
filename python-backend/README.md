# Python Backend

## Setup

1. Create `.env` from `.env.example` and fill Twilio credentials.
2. Install dependencies:

```bash
uv sync
```

3. Run the API:

```bash
uv run uvicorn mobile_otp.main:app --reload
```

The database tables are created at startup. You can also run:

```bash
uv run python -m mobile_otp.db.init_db
```

## Endpoints

- `POST /otp/send`
- `POST /otp/verify`
- `GET /health`