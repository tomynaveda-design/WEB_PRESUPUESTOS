from flask import Flask, redirect, url_for
from app.extensions import db
from app.routes.consumos import consumos_bp
from app.routes.obras import obras_bp
from app.routes.materiales import materiales_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuraciones
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/gestion_obras'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Registro de Blueprints
app.register_blueprint(consumos_bp)
app.register_blueprint(obras_bp)
app.register_blueprint(materiales_bp)

@app.route('/')
def home():
    return redirect(url_for('obras.index'))

if __name__ == '__main__':
    app.run(debug=True)