from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import InventarioGalpon

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
def index():
    materiales = InventarioGalpon.query.order_by(InventarioGalpon.id.asc()).all()
    
    # Métricas para tarjetas superiores
    total_items = len(materiales)
    total_stock = sum(m.cantidad for m in materiales if m.cantidad > 0)
    items_sin_stock = sum(1 for m in materiales if m.cantidad <= 0)

    return render_template(
        'inventario/index.html', 
        materiales=materiales,
        total_items=total_items,
        total_stock=total_stock,
        items_sin_stock=items_sin_stock
    )

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
    
    # Se actualizan todos los campos editables
    material.articulo = request.form.get('articulo', material.articulo)
    try:
        material.cantidad = float(request.form.get('cantidad', material.cantidad))
    except (ValueError, TypeError):
        pass
    material.observaciones = request.form.get('observaciones', material.observaciones)
    
    db.session.commit()
    flash('Inventario actualizado correctamente.', 'success')
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    material = InventarioGalpon.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('Material eliminado del inventario.', 'danger')
    return redirect(url_for('inventario.index'))