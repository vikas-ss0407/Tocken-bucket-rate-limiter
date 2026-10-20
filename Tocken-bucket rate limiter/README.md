# Token-Bucket Rate Limiter API

A lightweight REST API built with **Python and FastAPI** that limits client requests using the Token-Bucket algorithm. It supports bucket configuration, token consumption, automatic token refilling, and rate-limit responses.

## Features

- Configure a token bucket for each client.
- Set bucket capacity, refill rate, and refill interval.
- Allow requests when tokens are available.
- Return HTTP `429 Too Many Requests` when the bucket is empty.
- Include a `Retry-After` response header when a request is rate-limited.
- Check the current bucket status and available tokens.
- Includes automated tests using pytest.

## Requirements

- Python 3
- pip

## Installation

Clone the repository and navigate to the project directory:

```powershell
git clone <your-github-repository-url>
cd <your-project-folder>
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## Run Tests

Open another terminal in the project directory, activate the virtual environment, and run:

```powershell
python -m pytest -v
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/api/limit/configure` | Configure or reset a client's bucket |
| POST | `/api/limit/{client_id}` | Consume one token |
| GET | `/api/limit/{client_id}` | Check bucket status |

### 1. Configure a Bucket

**POST** `/api/limit/configure`

Example request:

```json
{
  "client_id": "user1",
  "capacity": 3,
  "refill_rate": 1,
  "refill_interval_seconds": 10
}
```

This creates a bucket with a maximum capacity of 3 tokens and refills at a rate of 1 token every 10 seconds.

### 2. Consume a Token

**POST** `/api/limit/user1`

- **HTTP 200:** A token is available and the request is allowed.
- **HTTP 429:** No token is available; the request is rate-limited.
- **HTTP 404:** The client's bucket has not been configured.

A rate-limited response includes a `Retry-After` header.

### 3. Check Bucket Status

**GET** `/api/limit/user1`

Returns the bucket's capacity, refill settings, client ID, and current available tokens.

## Testing

The automated tests cover:

- Bucket configuration.
- Requests allowed while tokens are available.
- Rate limiting when tokens are exhausted.
- Handling unknown clients.
- Checking bucket status.
- Token refilling after time passes.

## Design Decisions and Limitations

- **Storage:** An in-memory Python dictionary.
- **Database:** No database server required.
- **Authentication:** Not included.
- **Frontend:** Not included; FastAPI provides interactive API documentation.
- **Persistence:** Bucket data resets when the application restarts.
- **Deployment:** Designed for a local, single-instance demonstration.
- **Distributed rate limiting:** Not supported; multiple application instances would maintain separate bucket states.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- pytest
- HTTPX

## License

No license has been specified. Add a license if you intend to allow others to reuse or distribute this project.