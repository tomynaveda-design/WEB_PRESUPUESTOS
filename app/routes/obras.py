from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from app.models import Obra

# Definimos el Blueprint para obras
obras_bp = Blueprint('obras', __name__)

@obras_bp.route('/')
def index():
    # Consultamos todas las obras activas
    obras_list = Obra.query.filter_by(activo=True).all()
    return render_template('obras/index.html', obras=obras_list)

@obras_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        presupuesto_inicial = request.form.get('presupuesto_inicial')

        # Creamos la nueva obra con los datos del formulario
        nueva_obra = Obra(
            nombre=nombre,
            descripcion=descripcion,
            presupuesto_inicial=float(presupuesto_inicial)
        )
        
        db.session.add(nueva_obra)
        db.session.commit()
        
        return redirect(url_for('obras.index'))

    return render_template('obras/crear.html')