import os
from flask import Flask, redirect, url_for
from app.extensions import db
from app.routes.consumos import consumos_bp
from app.routes.obras import obras_bp
from app.routes.materiales import materiales_bp
from app.routes.inventario import inventario_bp  # <-- 1. Importarlo acá
from app.models import InventarioGalpon  # <-- Agregá esta línea con tus imports

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuraciones
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# CONFIGURACIÓN DE BASE DE DATOS (Toma la del .env o usa SQLite por defecto si no existe)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gestion_obras.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Registro de Blueprints
app.register_blueprint(consumos_bp)
app.register_blueprint(obras_bp)
app.register_blueprint(materiales_bp)
app.register_blueprint(inventario_bp)  # <-- 2. Registrarlo acá

# Crear tablas automáticamente al arrancar si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('obras.index'))

if __name__ == '__main__':
    # Puerto dinámico para Render y escucha en 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)