# URL Shortener

A URL shortening service built with Flask and Redis that generates 6-character short codes with TTL-based expiry, custom codes, click tracking, and sub-10ms redirect lookups.

## Tech Stack
- **Framework:** Flask 3
- **Storage:** Redis 7
- **Container:** Docker + docker-compose
- **Testing:** pytest + fakeredis

## Features
- Auto-generated 6-character short codes
- Custom short codes with collision detection
- TTL-based link expiry (default 1 day)
- Click tracking via Redis atomic counters
- Stats endpoint (`/stats/<code>`)
- One-command Docker setup

## Project Structure
```
url_shortener/
├── app.py            # Application factory
├── extensions.py     # Redis client init
├── routes.py         # Endpoints
└── tests/test_api.py # Unit tests
```

## Setup

### Local (Redis must be running)
```bash
git clone https://github.com/<your-username>/url_shortener.git
cd url_shortener
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
redis-server &   # or: docker run -p 6379:6379 redis
python app.py
```

### Docker (recommended)
```bash
docker-compose up --build
```

Server runs at `http://localhost:5000`.

## Run Tests
```bash
pytest -v
```

## API Endpoints

| Method | Endpoint       | Description                       | Body                                                    |
|--------|----------------|-----------------------------------|---------------------------------------------------------|
| POST   | /shorten       | Create a short URL                | `{"url": "https://...", "custom": "abc", "ttl": 3600}`  |
| GET    | /\<code\>      | Redirect to original URL          | —                                                       |
| GET    | /stats/\<code\>| Get URL + click count + TTL       | —                                                       |

### Sample Requests

```bash
# Shorten
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Response:
# {"short": "http://localhost:5000/aB3xY9", "expires_in": 86400}

# Redirect
curl -L http://localhost:5000/aB3xY9

# Stats
curl http://localhost:5000/stats/aB3xY9
# {"code":"aB3xY9","url":"https://example.com","clicks":1,"ttl":86390}
```

## License
MIT
