from flask import Flask
from config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Importar y registrar el Blueprint de obras
    from app.routes.obras import obras_bp
    app.register_blueprint(obras_bp)

    return app