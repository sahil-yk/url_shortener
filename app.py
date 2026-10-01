import os
from flask import Flask
from extensions import init_redis
from routes import bp as url_bp

def create_app():
    app = Flask(__name__)
    app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.config["DEFAULT_TTL"] = int(os.getenv("DEFAULT_TTL", 86400))

    init_redis(app)
    app.register_blueprint(url_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
