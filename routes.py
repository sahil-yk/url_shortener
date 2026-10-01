import string, random
from flask import Blueprint, request, jsonify, redirect, current_app
import extensions

bp = Blueprint("urls", __name__)

def gen_code(n=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

@bp.post("/shorten")
def shorten():
    d = request.get_json() or {}
    url = d.get("url")
    if not url or not url.startswith("http"):
        return jsonify({"error": "valid url required"}), 400

    code = d.get("custom") or gen_code()
    if extensions.redis_client.exists(code):
        return jsonify({"error": "code taken"}), 409

    ttl = d.get("ttl", current_app.config["DEFAULT_TTL"])
    extensions.redis_client.setex(code, ttl, url)
    extensions.redis_client.set(f"clicks:{code}", 0, ex=ttl)
    return jsonify({
        "short": f"{current_app.config['BASE_URL']}/{code}",
        "expires_in": ttl
    }), 201

@bp.get("/<code>")
def go(code):
    url = extensions.redis_client.get(code)
    if not url:
        return jsonify({"error": "not found or expired"}), 404
    extensions.redis_client.incr(f"clicks:{code}")
    return redirect(url)

@bp.get("/stats/<code>")
def stats(code):
    url = extensions.redis_client.get(code)
    if not url:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "code": code,
        "url": url,
        "clicks": int(extensions.redis_client.get(f"clicks:{code}") or 0),
        "ttl": extensions.redis_client.ttl(code)
    })
