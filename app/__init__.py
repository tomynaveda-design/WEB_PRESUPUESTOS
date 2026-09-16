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

    from app.routes.obras import obras_bp
    from app.routes.materiales import materiales_bp
    from app.routes.consumos import consumos_bp
    from app.routes.inventario import inventario_bp

    app.register_blueprint(obras_bp)
    app.register_blueprint(materiales_bp)
    app.register_blueprint(consumos_bp)
    app.register_blueprint(inventario_bp)

    # <-- Agregá esto acá abajo:
    with app.app_context():
        db.create_all()

    return app