
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.rate_limiter import (
    configure_bucket,
    consume_token,
    get_bucket_status,
)

app = FastAPI(
    title="Token-Bucket Rate Limiter API",
    description="A small API for controlling request rates per client.",
    version="1.0.0",
)


class BucketConfig(BaseModel):
    client_id: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0)
    refill_rate: float = Field(gt=0, allow_inf_nan=False)
    refill_interval_seconds: float = Field(
        gt=0, allow_inf_nan=False
    )


@app.get("/")
def root():
    return {"message": "Token-Bucket Rate Limiter API is running"}


@app.post("/api/limit/configure", status_code=201)
def configure_limit(config: BucketConfig):
    client_id = config.client_id.strip()

    if not client_id:
        raise HTTPException(
            status_code=422,
            detail="client_id cannot be blank",
        )

    status = configure_bucket(
        client_id=client_id,
        capacity=config.capacity,
        refill_rate=config.refill_rate,
        refill_interval_seconds=config.refill_interval_seconds,
    )

    return {
        "message": "Bucket configured successfully",
        **status,
    }


@app.post("/api/limit/{client_id}")
def check_limit(client_id: str):
    result = consume_token(client_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Client bucket not found. Configure it first.",
        )

    if not result["allowed"]:
        retry_after = result["retry_after_seconds"]

        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content={
                "client_id": client_id,
                "allowed": False,
                "remaining_tokens": 0,
                "retry_after_seconds": retry_after,
                "message": "Rate limit exceeded",
            },
        )

    return {
        "client_id": client_id,
        **result,
        "message": "Request allowed",
    }


@app.get("/api/limit/{client_id}")
def limit_status(client_id: str):
    status = get_bucket_status(client_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Client bucket not found. Configure it first.",
        )

    return status
