import re
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Obra, ObraMaterial, Proveedor, CotizacionProveedor

obras_bp = Blueprint('obras', __name__)

@obras_bp.route('/')
def index():
    obras_list = Obra.query.filter_by(activo=True).all()
    return render_template('obras/index.html', obras=obras_list)

@obras_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        presupuesto_raw = request.form.get('presupuesto_inicial')
        presupuesto_inicial = float(presupuesto_raw) if presupuesto_raw else 0.0

        nueva_obra = Obra(
            nombre=nombre,
            descripcion=descripcion,
            presupuesto_inicial=presupuesto_inicial
        )
        
        db.session.add(nueva_obra)
        db.session.commit()
        return redirect(url_for('obras.index'))

    return render_template('obras/crear.html')

@obras_bp.route('/<int:id>')
def detalle(id):
    obra = Obra.query.get_or_404(id)
    return render_template('obras/detalle.html', obra=obra)

@obras_bp.route('/<int:id>/agregar_material', methods=['GET', 'POST'])
def agregar_material(id):
    obra = Obra.query.get_or_404(id)
    
    if request.method == 'POST':
        nuevo_material = ObraMaterial(
            obra_id=obra.id,
            codigo=request.form.get('codigo'),
            articulo=request.form.get('articulo'),
            marca=request.form.get('marca'),
            cantidad_presupuestada=float(request.form.get('cantidad')),
            cantidad_disponible=float(request.form.get('cantidad')),
            unidad_medida=request.form.get('unidad_medida'),
            etapa=request.form.get('etapa')
        )
        db.session.add(nuevo_material)
        db.session.commit()
        return redirect(url_for('obras.detalle', id=obra.id))
        
    return render_template('obras/agregar_material.html', obra=obra)

# NUEVA RUTA: Editar Material
@obras_bp.route('/material/<int:material_id>/editar', methods=['GET', 'POST'])
def editar_material(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    if request.method == 'POST':
        material.codigo = request.form.get('codigo')
        material.articulo = request.form.get('articulo')
        material.marca = request.form.get('marca')
        
        nueva_cant = float(request.form.get('cantidad', 0))
        material.cantidad_presupuestada = nueva_cant
        material.cantidad_disponible = nueva_cant
        material.unidad_medida = request.form.get('unidad_medida')
        material.etapa = request.form.get('etapa')
        
        # Si cambia la cantidad, recalcula los totales de las cotizaciones guardadas
        for cot in material.cotizaciones:
            cot.precio_total = nueva_cant * cot.precio_unitario
            
        db.session.commit()
        return redirect(url_for('obras.detalle', id=material.obra_id))
        
    return render_template('obras/editar_material.html', material=material)

# NUEVA RUTA: Eliminar Material
@obras_bp.route('/material/<int:material_id>/eliminar', methods=['POST'])
def eliminar_material(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    obra_id = material.obra_id
    
    # Borramos primero las cotizaciones asociadas a este material
    CotizacionProveedor.query.filter_by(obra_material_id=material.id).delete()
    
    db.session.delete(material)
    db.session.commit()
    
    return redirect(url_for('obras.detalle', id=obra_id))

@obras_bp.route('/<int:id>/importar', methods=['POST'])
def importar_excel(id):
    obra = Obra.query.get_or_404(id)
    archivo = request.files.get('documento_excel')
    
    if archivo:
        try:
            df = pd.read_excel(archivo)
            df.columns = df.columns.str.strip().str.upper()
            
            for index, row in df.iterrows():
                articulo = str(row.get('ARTÍCULO', row.get('ARTICULO', ''))).strip()
                if not articulo or articulo == 'nan':
                    continue
                    
                cantidad_raw = str(row.get('CANTIDAD', '0')).strip()
                match = re.search(r'[\d\.]+', cantidad_raw)
                cantidad_num = float(match.group()) if match else 0.0
                
                unidad_texto = re.sub(r'[\d\.]+', '', cantidad_raw).strip()
                if not unidad_texto:
                    unidad_texto = 'unidades'
                    
                codigo_raw = str(row.get('CODIGO', row.get('CÓDIGO', ''))).replace('.0', '').replace('nan', '')
                marca_raw = str(row.get('MARCA', '')).replace('nan', '')
                etapa_raw = str(row.get('ETAPA', '')).replace('nan', '')

                nuevo_material = ObraMaterial(
                    obra_id=obra.id,
                    codigo=codigo_raw,
                    articulo=articulo,
                    marca=marca_raw,
                    cantidad_presupuestada=cantidad_num,
                    cantidad_disponible=cantidad_num,
                    unidad_medida=unidad_texto,
                    etapa=etapa_raw
                )
                db.session.add(nuevo_material)
            
            db.session.commit()
        except Exception as e:
            print(f"Error al leer Excel: {e}")
            
    return redirect(url_for('obras.detalle', id=obra.id))

# Ruta para cargar los precios de los 3 proveedores de un material
@obras_bp.route('/material/<int:material_id>/cotizar', methods=['GET', 'POST'])
def cotizar_material(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    if request.method == 'POST':
        # Reemplazamos las cotizaciones previas de este material para evitar duplicados
        CotizacionProveedor.query.filter_by(obra_material_id=material.id).delete()
        
        for i in range(1, 4):
            prov_nombre = request.form.get(f'proveedor_{i}', '').strip()
            precio_u_str = request.form.get(f'precio_{i}', '').strip()
            
            if prov_nombre and precio_u_str:
                precio_u = float(precio_u_str)
                
                # Buscamos si el proveedor ya existe en la base, sino lo creamos
                proveedor = Proveedor.query.filter_by(nombre=prov_nombre).first()
                if not proveedor:
                    proveedor = Proveedor(nombre=prov_nombre)
                    db.session.add(proveedor)
                    db.session.commit()
                
                total = material.cantidad_presupuestada * precio_u
                
                cotizacion = CotizacionProveedor(
                    obra_material_id=material.id,
                    proveedor_id=proveedor.id,
                    precio_unitario=precio_u,
                    precio_total=total
                )
                db.session.add(cotizacion)
                
        db.session.commit()
        return redirect(url_for('obras.detalle', id=material.obra_id))
        
    # Consultamos todos los proveedores registrados ordenados alfabéticamente
    proveedores = Proveedor.query.order_by(Proveedor.nombre.asc()).all()
    cotizaciones_existentes = material.cotizaciones
    
    return render_template('obras/cotizar.html', material=material, proveedores=proveedores, cotizaciones=cotizaciones_existentes)