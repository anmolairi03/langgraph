# URL Shortener

A full-stack URL shortener built to learn and demonstrate core system design concepts: REST API design, caching strategy, persistent storage, and containerized deployment.

## Architecture

```
┌─────────────┐      HTTP       ┌─────────────┐
│  Streamlit   │ ───────────────▶│   FastAPI    │
│  (Frontend)  │                 │   (Backend)  │
└─────────────┘                 └──────┬───────┘
                                        │
                          ┌─────────────┼─────────────┐
                          ▼                           ▼
                   ┌─────────────┐            ┌─────────────┐
                   │    Redis     │            │  PostgreSQL  │
                   │   (Cache)    │            │  (Database)  │
                   └─────────────┘            └─────────────┘
```

- **Frontend (Streamlit):** takes a long URL from the user, calls the backend API, displays the shortened URL.
- **Backend (FastAPI):** generates short codes, validates input, serves redirects, tracks click counts.
- **PostgreSQL:** the permanent source of truth — every short URL mapping and its click count lives here.
- **Redis:** a cache-aside layer in front of Postgres, so repeated redirects for the same short code don't hit the database every time.

All four services run in Docker containers, orchestrated with Docker Compose.

## Features

- Shorten any valid URL via a REST API (`POST /shorten`)
- Redirect from a short code to the original URL (`GET /{short_code}`), using a real HTTP 302 redirect
- Collision-safe short code generation (random 6-character alphanumeric codes, checked against the database before use)
- Request/response validation with Pydantic (`HttpUrl` type — rejects malformed URLs before they ever reach business logic)
- Redis caching with a cache-aside pattern and TTL-based expiration
- Click count tracking per short URL
- Simple Streamlit UI for creating and copying short links
- Fully containerized with Docker Compose, including Postgres/Redis health checks so the backend doesn't start before its dependencies are actually ready

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | PostgreSQL (via SQLAlchemy ORM) |
| Cache | Redis |
| Deployment | Docker, Docker Compose |

## Design Decisions & Tradeoffs

A few deliberate choices worth noting (the kind of thing worth discussing in an interview):

- **302, not 301, for redirects.** A 301 (permanent redirect) tells browsers to cache the redirect and stop asking the server — which would break click tracking, since the server would never see repeat visits. 302 ensures every click is actually seen and counted.
- **Duplicate long URLs get separate short codes.** Simpler to reason about, and it means click analytics are meaningful per-link rather than shared across everyone who happened to shorten the same URL.
- **`id` (auto-increment integer) as the primary key, not `short_code`.** Keeps the row's internal identity stable even if a short code ever needs to be regenerated, and integer comparisons/joins are cheaper than string ones at scale.
- **Click counts are updated synchronously in Postgres on every request (cache hit or miss).** This is the simple, always-accurate approach for v1. A production system at higher scale would likely buffer click counts in Redis and periodically sync them to Postgres in a batch — trading perfect real-time accuracy for far fewer writes (an "eventual consistency" / write-behind caching pattern). Noted here as a known, deliberate scope decision rather than an oversight.
- **Fixed TTL (1 hour) for cached entries**, rather than sliding expiration. Simpler for v1; refreshing the TTL on every cache hit (so popular links stay cached longer) is a natural follow-up improvement.

## Project Structure

```
url_shortner/
├── backend/
│   ├── main.py           # FastAPI app, endpoints
│   ├── db.py             # SQLAlchemy model, engine, session
│   ├── utils.py          # Pydantic models, short code generation
│   ├── caching.py        # Redis connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── frontend.py        # Streamlit UI
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Running the Project

**Prerequisites:** Docker and Docker Compose installed.

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in real values (or use the defaults for local development)
3. From the project root:
   ```bash
   docker-compose up --build
   ```
4. Open:
   - Streamlit UI: [http://localhost:8501](http://localhost:8501)
   - FastAPI docs: [http://localhost:8888/docs](http://localhost:8888/docs)

## API Reference

### `POST /shorten`

Request body:
```json
{
  "long_url": "https://example.com/some/long/path"
}
```

Response:
```json
{
  "long_url": "https://example.com/some/long/path",
  "short_url": "http://localhost:8888/aB3xY9",
  "short_code": "aB3xY9"
}
```

### `GET /{short_code}`

Redirects (HTTP 302) to the original long URL, or returns a 404 if the short code doesn't exist.

## Known Limitations / Future Improvements

- No authentication — anyone can create short URLs (would need user accounts + auth to attribute links to users)
- Click counts are written synchronously to Postgres on every request; a write-behind Redis buffer with periodic sync would reduce database load at scale
- No custom aliases (users can't choose their own short code)
- No rate limiting
- No expiration for short URLs themselves (only the Redis cache entries expire, not the underlying database rows)
