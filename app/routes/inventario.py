from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import InventarioGalpon

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
def index():
    # Traemos los materiales ordenados por ID de forma ascendente (1, 2, 3...)
    materiales = InventarioGalpon.query.order_by(InventarioGalpon.id.asc()).all()
    return render_template('inventario/index.html', materiales=materiales)

@inventario_bp.route('/agregar', methods=['POST'])
def agregar():
    articulo = request.form.get('articulo')
    cantidad = request.form.get('cantidad', 0)
    observaciones = request.form.get('observaciones')

    nuevo = InventarioGalpon(
        articulo=articulo,
        cantidad=float(cantidad) if cantidad else 0.0,
        observaciones=observaciones
    )
    db.session.add(nuevo)
    db.session.commit()
    flash('Material agregado correctamente al inventario.', 'success')
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    material = InventarioGalpon.query.get_or_404(id)
    material.cantidad = request.form.get('cantidad', material.cantidad)
    material.observaciones = request.form.get('observaciones', material.observaciones)
    db.session.commit()
    flash('Inventario actualizado.', 'success')
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    material = InventarioGalpon.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('Material eliminado.', 'danger')
    return redirect(url_for('inventario.index'))