
import time

buckets = {}


def configure_bucket(
    client_id: str,
    capacity: int,
    refill_rate: float,
    refill_interval_seconds: float,
) -> dict:
    """Create or reset a client's token bucket."""
    buckets[client_id] = {
        "capacity": capacity,
        "refill_rate": refill_rate,
        "refill_interval_seconds": refill_interval_seconds,
        "tokens": float(capacity),
        "last_refill_at": time.monotonic(),
    }

    return get_bucket_status(client_id)


def _refill_bucket(bucket: dict) -> None:
    """Add tokens according to elapsed time."""
    now = time.monotonic()
    elapsed = max(0.0, now - bucket["last_refill_at"])

    interval = bucket["refill_interval_seconds"]
    tokens_to_add = (elapsed / interval) * bucket["refill_rate"]

    bucket["tokens"] = min(
        bucket["capacity"],
        bucket["tokens"] + tokens_to_add,
    )
    bucket["last_refill_at"] = now


def consume_token(client_id: str):
    """Consume one token or return retry information."""
    bucket = buckets.get(client_id)

    if bucket is None:
        return None

    _refill_bucket(bucket)

    if bucket["tokens"] >= 1:
        bucket["tokens"] -= 1

        return {
            "allowed": True,
            "remaining_tokens": int(bucket["tokens"]),
        }

    seconds_until_token = (
        (1 - bucket["tokens"])
        / bucket["refill_rate"]
        * bucket["refill_interval_seconds"]
    )

    return {
        "allowed": False,
        "remaining_tokens": 0,
        "retry_after_seconds": max(
            1, int(seconds_until_token) + (
                1 if seconds_until_token % 1 else 0
            )
        ),
    }


def get_bucket_status(client_id: str):
    """Return a client's current bucket status."""
    bucket = buckets.get(client_id)

    if bucket is None:
        return None

    _refill_bucket(bucket)

    return {
        "client_id": client_id,
        "capacity": bucket["capacity"],
        "refill_rate": bucket["refill_rate"],
        "refill_interval_seconds": bucket[
            "refill_interval_seconds"
        ],
        "available_tokens": round(bucket["tokens"], 2),
    }
