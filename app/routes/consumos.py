from flask import Blueprint, request, redirect, url_for, flash
from app.extensions import db
from app.models import ObraMaterial, RegistroUso

consumos_bp = Blueprint('consumos', __name__, url_prefix='/consumos')

@consumos_bp.route('/<int:material_id>/registrar_uso', methods=['POST'])
def registrar_uso(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    try:
        cantidad_usada = float(request.form.get('cantidad_usada', 0))
    except ValueError:
        cantidad_usada = 0.0
        
    notas = request.form.get('notas', '')

    if cantidad_usada <= 0:
        flash('Ingresá una cantidad válida.', 'warning')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    if cantidad_usada > material.cantidad_disponible:
        flash(f'No podés usar {cantidad_usada} {material.unidad_medida}. Solo tenés {material.cantidad_disponible} en stock.', 'danger')
        return redirect(url_for('obras.detalle', id=material.obra_id))

    # Valorización real del consumo basado en el precio vigente
    costo_calculado = cantidad_usada * material.precio_unitario_vigente

    registro = RegistroUso(
        obra_material_id=material.id,
        cantidad_usada=cantidad_usada,
        costo_total=costo_calculado,
        notas=notas
    )
    
    db.session.add(registro)
    db.session.commit()
    
    flash('Consumo registrado y valorizado en la obra.', 'success')
    return redirect(url_for('obras.detalle', id=material.obra_id))


@consumos_bp.route('/<int:uso_id>/eliminar', methods=['POST'])
def eliminar_uso(uso_id):
    registro = RegistroUso.query.get_or_404(uso_id)
    obra_id = registro.obra_material.obra_id
    
    db.session.delete(registro)
    db.session.commit()
    
    flash('Registro de uso eliminado y stock restaurado.', 'success')
    return redirect(url_for('obras.detalle', id=obra_id))


@consumos_bp.route('/material/<int:material_id>/resetear', methods=['POST'])
def resetear_uso_material(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    for registro in material.registros_uso:
        db.session.delete(registro)
        
    db.session.commit()
    
    flash(f'Se eliminó todo el historial de uso para {material.articulo}.', 'success')
    return redirect(url_for('obras.detalle', id=material.obra_id))