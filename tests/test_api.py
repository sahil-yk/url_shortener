import pytest
import fakeredis
from app import create_app
import extensions


@pytest.fixture
def client(monkeypatch):
    # Use in-memory fake Redis for tests
    fake = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(extensions, "redis_client", fake)

    app = create_app()
    app.config["TESTING"] = True
    app.config["BASE_URL"] = "http://testserver"
    with app.test_client() as c:
        yield c


def test_shorten_url(client):
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["short"].startswith("http://testserver/")
    assert body["expires_in"] > 0


def test_shorten_invalid_url(client):
    r = client.post("/shorten", json={"url": "not-a-url"})
    assert r.status_code == 400


def test_redirect(client):
    short = client.post("/shorten", json={"url": "https://example.com"}).get_json()["short"]
    code = short.rsplit("/", 1)[-1]
    r = client.get(f"/{code}")
    assert r.status_code == 302
    assert r.headers["Location"] == "https://example.com"


def test_redirect_missing_code(client):
    r = client.get("/doesnotexist")
    assert r.status_code == 404


def test_custom_code(client):
    r = client.post("/shorten", json={"url": "https://example.com", "custom": "mylink"})
    assert r.status_code == 201
    assert "mylink" in r.get_json()["short"]


def test_custom_code_conflict(client):
    client.post("/shorten", json={"url": "https://a.com", "custom": "dup"})
    r = client.post("/shorten", json={"url": "https://b.com", "custom": "dup"})
    assert r.status_code == 409


def test_stats(client):
    short = client.post("/shorten", json={"url": "https://example.com"}).get_json()["short"]
    code = short.rsplit("/", 1)[-1]
    client.get(f"/{code}")
    client.get(f"/{code}")
    r = client.get(f"/stats/{code}")
    body = r.get_json()
    assert body["url"] == "https://example.com"
    assert body["clicks"] == 2
