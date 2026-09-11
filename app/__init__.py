from flask import Flask
from config import Config
from app.extensions import db
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importar y registrar los Blueprints dentro del contexto de la app
    from app.routes.obras import obras_bp
    from app.routes.materiales import materiales_bp
    from app.routes.consumos import consumos_bp

    app.register_blueprint(obras_bp)
    app.register_blueprint(materiales_bp)
    app.register_blueprint(consumos_bp)

    return app