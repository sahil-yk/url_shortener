import redis
from flask import current_app

# Single module-level holder
redis_client = None

def init_redis(app):
    """Called once from create_app() to set up the real client."""
    global redis_client
    redis_client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)