from flask import Flask

from .config import DATA_DIR
from .init_db import init_database
from .routes.contents import bp as contents_bp
from .routes.health import bp as health_bp
from .routes.platforms import bp as platforms_bp
from .routes.publish import bp as publish_bp


def create_app():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    init_database()
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    app.register_blueprint(contents_bp)
    app.register_blueprint(platforms_bp)
    app.register_blueprint(publish_bp)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5409, debug=True)
