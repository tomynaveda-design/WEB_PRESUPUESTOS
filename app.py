import os
from flask import Flask, redirect, url_for
from app.extensions import db
from app.routes.consumos import consumos_bp
from app.routes.obras import obras_bp
from app.routes.materiales import materiales_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuraciones
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# BASE DE DATOS:
# En producción (Render) usará una variable DATABASE_URL si la configuras.
# Si no hay variable definida, usará SQLite ('sqlite:///gestion_obras.db') para que la web funcione inmediatamente sin errores de localhost.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gestion_obras.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Crea las tablas automáticamente al iniciar si usas SQLite
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
    # Lee el puerto asignado por Render (PORT) y abre la escucha en 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)