import os
from flask import Flask, redirect, url_for
from app.extensions import db
from app.routes.consumos import consumos_bp
from app.routes.obras import obras_bp
from app.routes.materiales import materiales_bp
from app.routes.inventario import inventario_bp
from app.models import InventarioGalpon

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuraciones
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# CONFIGURACIÓN DE BASE DE DATOS (Usando _v3 para garantizar un archivo 100% nuevo y limpio)
# CONFIGURACIÓN DE BASE DE DATOS (Forzamos la base de datos nueva para que cree la columna observaciones)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestion_obras_v3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Registro de Blueprints
app.register_blueprint(consumos_bp)
app.register_blueprint(obras_bp)
app.register_blueprint(materiales_bp)
app.register_blueprint(inventario_bp)

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