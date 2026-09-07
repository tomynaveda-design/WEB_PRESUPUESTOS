from app.extensions import db
from datetime import datetime

class Obra(db.Model):
    __tablename__ = 'obras'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    presupuesto_inicial = db.Column(db.Numeric(12, 2), default=0.0)
    estado = db.Column(db.String(50), default='En curso')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con los materiales asignados a esta obra
    materiales = db.relationship('ObraMaterial', backref='obra', cascade='all, delete-orphan', lazy=True)


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    telefono = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Relación con sus cotizaciones
    cotizaciones = db.relationship('CotizacionProveedor', backref='proveedor', lazy=True)


class ObraMaterial(db.Model):
    __tablename__ = 'obra_material'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    
    codigo = db.Column(db.String(50), nullable=True)           # Ej: "1", "2", "A1"
    articulo = db.Column(db.String(150), nullable=False)        # Ej: "Hierro Nervado 6mm"
    marca = db.Column(db.String(100), nullable=True)            # Ej: "Acindar"
    cantidad_presupuestada = db.Column(db.Float, nullable=False) # Ej: 75
    cantidad_disponible = db.Column(db.Float, nullable=False)   # Se descuenta al usarse
    unidad_medida = db.Column(db.String(50), nullable=False)    # Ej: "var", "kg", "m3"
    etapa = db.Column(db.String(100), nullable=True)            # Ej: "1,2,3,4" o "5"
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    cotizaciones = db.relationship('CotizacionProveedor', backref='obra_material', cascade='all, delete-orphan', lazy=True)
    registros_uso = db.relationship('RegistroUso', backref='obra_material', cascade='all, delete-orphan', lazy=True)

    def cotizacion_mas_barata(self):
        """Retorna la cotización con el precio unitario más bajo para este material."""
        if not self.cotizaciones:
            return None
        return min(self.cotizaciones, key=lambda c: c.precio_unitario)


class CotizacionProveedor(db.Model):
    __tablename__ = 'cotizacion_proveedor'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_material_id = db.Column(db.Integer, db.ForeignKey('obra_material.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    precio_total = db.Column(db.Numeric(12, 2), nullable=False) # precio_unitario * cantidad_presupuestada
    es_seleccionado = db.Column(db.Boolean, default=False)      # Para marcar cuál se compró/eligió finalmente


class RegistroUso(db.Model):
    __tablename__ = 'registro_uso'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_material_id = db.Column(db.Integer, db.ForeignKey('obra_material.id'), nullable=False)
    cantidad_usada = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_uso = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text, nullable=True)