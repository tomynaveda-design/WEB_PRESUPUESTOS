# app/routes/materiales.py
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

    if cantidad_nueva <= 0:
        flash('Ingresá una cantidad válida para la compra.', 'warning')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    # Sumamos solo a lo comprado. El stock disponible se calcula solo.
    material.cantidad_comprada += cantidad_nueva
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

    if nueva_cantidad < 0:
        flash('La cantidad comprada no puede ser negativa.', 'warning')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    material.cantidad_comprada = nueva_cantidad
    material.actualizar_estado_compra()

    db.session.commit()
    flash('Cantidad comprada actualizada correctamente.', 'success')
    return redirect(url_for('obras.detalle', id=material.obra_id))