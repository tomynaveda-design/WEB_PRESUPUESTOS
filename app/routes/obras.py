import re
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Obra, ObraMaterial, Proveedor, CotizacionProveedor
from app.models import InventarioGalpon

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/inventario')
def index():
    # Traemos todos los materiales ordenados por el último actualizado
    materiales = InventarioGalpon.query.order_by(InventarioGalpon.fecha_actualizacion.desc()).all()
    return render_template('inventario/index.html', materiales=materiales)

@inventario_bp.route('/inventario/agregar', methods=['POST'])
def agregar():
    codigo = request.form.get('codigo')
    articulo = request.form.get('articulo')
    cantidad = request.form.get('cantidad', 0, type=float)
    unidad_medida = request.form.get('unidad_medida', 'Unidades')

    if articulo:
        nuevo_material = InventarioGalpon(
            codigo=codigo,
            articulo=articulo,
            cantidad=cantidad,
            unidad_medida=unidad_medida
        )
        db.session.add(nuevo_material)
        db.session.commit()
        flash('Material agregado al inventario.', 'success')
        
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/inventario/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    material = InventarioGalpon.query.get_or_404(id)
    nueva_cantidad = request.form.get('cantidad', type=float)
    
    if nueva_cantidad is not None:
        material.cantidad = nueva_cantidad
        db.session.commit()
        flash('Stock actualizado.', 'success')
        
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/inventario/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    material = InventarioGalpon.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('Material eliminado del inventario.', 'success')
    return redirect(url_for('inventario.index'))

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

@obras_bp.route('/eliminar/<int:id>', methods=['POST']) 
def eliminar_obra(id):
    obra = Obra.query.get_or_404(id)
    
    try:
        db.session.delete(obra)
        db.session.commit()
        flash('Obra eliminada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la obra. Verificá que no tenga materiales asociados.', 'danger')
        
    return redirect(url_for('obras.index'))

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
            unidad_medida=request.form.get('unidad_medida'),
            etapa=request.form.get('etapa')
        )
        db.session.add(nuevo_material)
        db.session.commit()
        return redirect(url_for('obras.detalle', id=obra.id))
        
    return render_template('obras/agregar_material.html', obra=obra)

# Ruta: Editar Material
@obras_bp.route('/material/<int:material_id>/editar', methods=['GET', 'POST'])
def editar_material(material_id):
    material = ObraMaterial.query.get_or_404(material_id)
    
    if request.method == 'POST':
        material.codigo = request.form.get('codigo')
        material.articulo = request.form.get('articulo')
        material.marca = request.form.get('marca')
        
        nueva_cant = float(request.form.get('cantidad', 0))
        material.cantidad_presupuestada = nueva_cant
        material.unidad_medida = request.form.get('unidad_medida')
        material.etapa = request.form.get('etapa')
        
        # Si cambia la cantidad, recalcula los totales de las cotizaciones guardadas
        for cot in material.cotizaciones:
            cot.precio_total = nueva_cant * cot.precio_unitario
            
        db.session.commit()
        return redirect(url_for('obras.detalle', id=material.obra_id))
        
    return render_template('obras/editar_material.html', material=material)

# Ruta: Eliminar Material
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
    
    print("--- INICIANDO IMPORTACIÓN ---")
    print("ARCHIVOS EN REQUEST.FILES:", request.files)
    
    archivo = request.files.get('documento_excel') or request.files.get('file')
    
    if not archivo or archivo.filename == '':
        print("ERROR: No se encontró ningún archivo en la petición.")
        flash('No se seleccionó ningún archivo de Excel.', 'danger')
        return redirect(url_for('obras.detalle', id=obra.id))

    print(f"ARCHIVO RECIBIDO: {archivo.filename}")

    try:
        df = pd.read_excel(archivo)
        # Normalizamos los nombres de las columnas (quitando espacios y pasando a mayúsculas)
        df.columns = [str(col).strip().upper() for col in df.columns]
        print("COLUMNAS DETECTADAS EN EL EXCEL:", list(df.columns))
        
        # Función auxiliar segura para extraer valores
        def obtener_valor(row, claves, por_defecto=""):
            for clave in claves:
                if clave in row:
                    val = row[clave]
                    # Validamos que no sea nulo ni NaN de pandas
                    if pd.notna(val) and str(val).strip().lower() != 'nan':
                        return str(val).strip()
            return por_defecto

        materiales_creados = 0

        for index, row in df.iterrows():
            # 1. ARTÍCULO (Campo obligatorio)
            articulo = obtener_valor(row, ['ARTÍCULO', 'ARTICULO', 'DESCRIPCIÓN', 'DESCRIPCION', 'MATERIAL'])
            if not articulo:
                continue
                
            # 2. CANTIDAD Y UNIDAD
            cant_val_crudo = obtener_valor(row, ['CANTIDAD', 'CANT', 'CANT.', 'CANTIDAD_PRESUPUESTADA', 'PRESUPUESTO'], por_defecto="0")
            unidad_medida = obtener_valor(row, ['UNIDAD', 'UNIDAD DE MEDIDA', 'UNIDAD_MEDIDA', 'U.M.', 'UM', 'MEDIDA'], por_defecto="Unidades")
            
            cantidad_num = 0.0
            cant_str = str(cant_val_crudo).replace(',', '.').strip()
            
            match = re.search(r'[\d\.]+', cant_str)
            if match:
                try:
                    cantidad_num = float(match.group())
                except ValueError:
                    cantidad_num = 0.0
            
            # Extraer unidad del texto de cantidad si no vino separada
            if unidad_medida == "Unidades" and cant_str:
                unidad_extraida = re.sub(r'[\d\.]+', '', cant_str).strip()
                if unidad_extraida:
                    unidad_medida = unidad_extraida

            # 3. OTROS CAMPOS
            codigo = obtener_valor(row, ['CÓDIGO', 'CODIGO', 'COD']).replace('.0', '')
            marca = obtener_valor(row, ['MARCA'])
            etapa = obtener_valor(row, ['ETAPA', 'RUBRO', 'CATEGORIA'])

            # Instanciamos el material
            nuevo_material = ObraMaterial(
                obra_id=obra.id,
                codigo=codigo if codigo != 'nan' else '',
                articulo=articulo,
                marca=marca if marca != 'nan' else '',
                cantidad_presupuestada=cantidad_num,
                unidad_medida=unidad_medida,
                etapa=etapa if etapa != 'nan' else ''
            )
            db.session.add(nuevo_material)
            materiales_creados += 1

        db.session.commit()
        print(f"¡ÉXITO! Se importaron {materiales_creados} materiales.")
        flash(f'¡Éxito! Se importaron {materiales_creados} materiales correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        print(f"EXCEPCIÓN EN IMPORTACIÓN: {str(e)}")
        flash(f'Error al procesar el archivo: {str(e)}', 'danger')
        
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