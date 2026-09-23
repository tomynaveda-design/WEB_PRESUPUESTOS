from flask import Blueprint, request, redirect, url_for, flash
from app.extensions import db
from app.models import ObraMaterial

materiales_bp = Blueprint('materiales', __name__, url_prefix='/materiales')

@materiales_bp.route('/<int:material_id>/registrar_compra', methods=['POST'])
def registrar_compra(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    try:
        cantidad_nueva = float(request.form.get('cantidad_comprada', 0))
    except ValueError:
        cantidad_nueva = 0.0

    precio_unitario_str = request.form.get('precio_unitario', '').strip()

    if cantidad_nueva <= 0:
        flash('Ingresá una cantidad válida para la compra.', 'warning')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    material.cantidad_comprada += cantidad_nueva
    
    # Si se especifica el precio real pagado, se guarda en el material
    if precio_unitario_str:
        try:
            material.precio_compra_unitario = float(precio_unitario_str)
        except ValueError:
            pass

    material.actualizar_estado_compra()

    db.session.commit()
    flash('Compra registrada y stock actualizado.', 'success')
    return redirect(url_for('obras.detalle', id=material.obra_id))

@materiales_bp.route('/<int:material_id>/editar_compra', methods=['POST'])
def editar_compra(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    try:
        nueva_cantidad = float(request.form.get('cantidad_comprada', 0))
    except ValueError:
        nueva_cantidad = 0.0

    precio_unitario_str = request.form.get('precio_unitario', '').strip()

    if nueva_cantidad < 0:
        flash('La cantidad comprada no puede ser negativa.', 'warning')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    material.cantidad_comprada = nueva_cantidad
    
    if precio_unitario_str:
        try:
            material.precio_compra_unitario = float(precio_unitario_str)
        except ValueError:
            pass

    material.actualizar_estado_compra()

    db.session.commit()
    flash('Cantidad y precio de compra actualizados correctamente.', 'success')
    return redirect(url_for('obras.detalle', id=material.obra_id))