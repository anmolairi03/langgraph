# rate-limiter

A reusable, framework-attachable rate limiter for FastAPI, built on the **token bucket** algorithm and backed by **Redis** (so it works correctly across multiple app instances, not just a single process).

## Features

- Token bucket algorithm — allows legitimate bursts, refills at a steady rate (no fixed-window boundary spikes).
- Redis-backed — safe for multi-instance deployments; each instance shares the same bucket state.
- Per-route limits — attach different limits to different endpoints independently.
- Standard `429 Too Many Requests` responses with a correctly formatted `Retry-After` header.
- No hardcoded Redis connection — you create and own the Redis client, the package just uses it (dependency injection), so it plays nicely alongside any other Redis usage in your app.

## Installation

```bash
pip install -e .
```

(Editable install, for local development. A future version can be published to PyPI for a normal `pip install rate-limiter`.)

## Requirements

- A running Redis instance, reachable from your app.
- FastAPI.

## Usage

```python
import redis
from fastapi import FastAPI, Depends
from rate_limiter import rate_limiter_dependency

app = FastAPI()

# You create and own the Redis client — the package never creates its own.
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.post("/login", dependencies=[Depends(rate_limiter_dependency(max_capacity=3, refill_rate=20, redis_client=redis_client))])
def login():
    return {"message": "login successful"}

@app.get("/test", dependencies=[Depends(rate_limiter_dependency(max_capacity=100, refill_rate=1, redis_client=redis_client))])
def test_endpoint():
    return {"message": "test successful"}
```

Each route gets its own independent limit — hitting `/test` doesn't consume tokens from `/login`'s bucket, and vice versa.

### Parameters

| Parameter | Meaning |
|---|---|
| `max_capacity` | Maximum tokens the bucket can hold — i.e. the size of an allowed burst. |
| `refill_rate` | Seconds it takes to earn back one token. |
| `redis_client` | A Redis client instance (e.g. from `redis.Redis(...)`) that you create and configure yourself. |

### Rejected requests

When a client exceeds their limit, they get:

```http
HTTP/1.1 429 Too Many Requests
retry-after: 16
content-type: application/json

{"detail": {"message": "Too many requests, wait for 16 before retrying"}}
```

`Retry-After` is always a whole number of seconds, per the HTTP spec.

## How it works

Each client (identified by IP address) has a "bucket" of tokens stored in Redis as a hash (`bucket:{ip}` → `{tokens, last_refill}`). On every request:

1. Elapsed time since the last request is calculated.
2. Tokens earned during that time (`elapsed_time / refill_rate`) are added back, capped at `max_capacity`.
3. If at least 1 token is available, it's spent and the request proceeds.
4. Otherwise, the request is rejected with a calculated wait time until the next token is available.

This "lazy refill" approach means there's no background job constantly running — the bucket only updates when a request actually arrives.

## Low-level API

If you're not using FastAPI, or want to build your own integration, the core calculation is also exposed directly:

```python
from rate_limiter import get_wait_time

wait_time = get_wait_time(ip="1.2.3.4", max_capacity=5, refill_rate=2, redis_client=redis_client)
# 0 if allowed, otherwise the number of seconds to wait
```

## Notes on Redis key namespacing

Keys are stored as `bucket:{ip}`. If you're running this alongside another app that uses the same Redis instance for other purposes (e.g. caching), make sure your key naming doesn't collide — this package doesn't currently support a configurable key prefix.

## Roadmap

- Configurable key prefix, for cleaner multi-app Redis sharing.
- API-key-based client identification, as an alternative to IP address.
- Published PyPI release.
