import os
from flask import Flask, redirect, url_for
from app.extensions import db
from app.routes.consumos import consumos_bp
from app.routes.obras import obras_bp
from app.routes.materiales import materiales_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuraciones
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# BASE DE DATOS FORZADA A SQLITE EN RENDER
db_url = os.environ.get('DATABASE_URL', '')
if not db_url or 'localhost' in db_url or '127.0.0.1' in db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestion_obras.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Crear tablas automáticamente si es SQLite
with app.app_context():
    db.create_all()

# Registro de Blueprints
app.register_blueprint(consumos_bp)
app.register_blueprint(obras_bp)
app.register_blueprint(materiales_bp)

@app.route('/')
def home():
    return redirect(url_for('obras.index'))

if __name__ == '__main__':
    # Puerto dinámico para Render y escucha en 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)